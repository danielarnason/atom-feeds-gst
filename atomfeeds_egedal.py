# coding: utf-8
#Dette script bygger videre på scriptet fra https://github.com/Kortforsyningen/utilities_and_example_implementations/tree/master/atomfeeds/Get_SHAPE_Matr_zip_from_Atomfeed_GST.py.
#Det som jeg har tilføjet er en txt fil, der siger, hvornår scriptet er kørt sidst, og en OGR2OGR statement, som smider de downloadede filer i en Postgis database.

import urllib
import xml.etree.ElementTree as ET
import datetime
import os
import ftplib
import traceback, sys
import glob
import zipfile

#I Ejerlav listen skal du skrive de ejerlav, der findes i din kommune
Ejerlav = ['21051', '21351', '21352', '21353', '21354', '21355', '80451', '80452', '80453', '80455', '80456', '90251', '90252', '90351', '90551', '90552', '90553', '90651', '90751', '90752', '90753']
# finder mappen hvor dette script er placeret
init_folder =  os.path.dirname(os.path.realpath(__file__))
# mappe hvor zipfiler downloades til
Output_folder =  init_folder + os.sep + "Til_Opdatering" 
logfil = init_folder + os.sep + "MatrikelDownload.log" 
#Her skal du erstatte XXX med dit brugernavn og password til Kortforsyningen
Brugernavn = "XXX"
Password = "XXX"

def read_Lastupdate(filepath):
	return datetime.datetime.fromtimestamp(os.path.getmtime(filepath))

def skriv_log(filepath, tekst):
    f = open(filepath, 'w')
    f.writelines(tekst)
    f.close

def hent_matr_zipfiler(ejerlav,Outputfolder, lastupdate):
    try:
        ftp = ftplib.FTP('ftp.kortforsyningen.dk', Brugernavn, Password)
        ftp.cwd('atomfeeds/MATRIKELKORT/ATOM/SHAPE')
        tree=ET.parse(urllib.urlopen("http://download.kortforsyningen.dk/sites/default/files/feeds/MATRIKELKORT_SHAPE.xml"))
        entries = tree.findall('{http://www.w3.org/2005/Atom}entry')
        for node in entries:
             id = node.find('{http://www.w3.org/2005/Atom}id')
             updated =node.find('{http://www.w3.org/2005/Atom}updated')
             zipurl = id.text
             dato=datetime.datetime.strptime(updated.text, "%Y-%m-%dT%H:%M:%S+01:00" )
             Ejerlavnr = zipurl[zipurl.find("SHAPE")+6:len(zipurl)-24]
             if Ejerlavnr in ejerlav:
                if dato  > lastupdate:
                   filename = Ejerlavnr + "_SHAPE_UTM32-EUREF89.zip"
                   file = open(Outputfolder + os.sep + filename, 'wb')
                   ftp.retrbinary('RETR %s' % filename, file.write)
                   skriv_log(logfil, "downloader ejerlav : " + Ejerlavnr + " opdatering d. " + str(dato) + '\n' )
                   file.close
        ftp.close
    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        print tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)

try:
    if not os.path.isfile(logfil):
        file = open(logfil, 'w+')
		#file.close
    Lastupdate =read_Lastupdate(logfil)
    if not os.path.exists(Output_folder):
        os.makedirs(Output_folder)
    hent_matr_zipfiler(Ejerlav, Output_folder,Lastupdate)

except:
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)

    print pymsg

#unzip files
zip_files = glob.glob(os.path.dirname(os.path.realpath(__file__)) + os.sep + "Til_Opdatering" + os.sep + '*.zip')

for zip_filename in zip_files:
    zip_dir = os.path.splitext(zip_filename)[0]
    file_name = os.path.split(zip_dir)[1]
    ejerlav_nr = file_name[:5]

    zip_handler = zipfile.ZipFile(zip_filename, "r")
    zip_handler.extractall(zip_dir)

    shp_dir = zip_dir + os.sep + file_name + os.sep + "MINIMAKS" + os.sep + "BASIS"
    shp_files = glob.glob(shp_dir + os.sep + "JORDSTYKKE.shp")
    
    #OGR2OGR to Postgis
    encoding_command = "set pgclientencoding=latin1"
    ogr2ogr = "ogr2ogr -f \"PostgreSQL\" PG:\"host=XXX port=XXX dbname=XXX user=XXX password=XXX\" " + shp_files[0] + " -nln XXXSKEMANAVNXXX.ejerlav_" + str(ejerlav_nr) + " -a_srs \"EPSG:25832\" -overwrite"
    os.system(encoding_command + ' & ' + ogr2ogr)
    
#skriv sidste tjek i textfil
last_tjek_f = init_folder + os.sep + 'sidste_tjek.txt'
last_tjek = open(last_tjek_f, 'a')
last_tjek.writelines("\nLast run: " + datetime.datetime.now().date().isoformat())
last_tjek.close
