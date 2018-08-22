"""
File: atomfeeds_egekom.py
Author: Me
Email: yourname@email.com
Github: https://github.com/yourname
Description: Et script, der kan downloade matrikler fra SDFE's atom feeds.
"""

import urllib.request
import os
import datetime
import logging
import ftplib
import config
import xml.etree.ElementTree as ET

ejerlav = ['21051', '21351', '21352', '21353', '21354', '21355', '80451', '80452', '80453', '80455', '80456', '90251', '90252', '90351', '90551', '90552', '90553', '90651', '90751', '90752', '90753']

init_folder = os.path.dirname(os.path.realpath(__file__))

output_folder = init_folder + os.sep + "til_opdatering"
logfil = init_folder + os.sep + "matrikeldownload.log"

def read_lastupdate(filepath):
    """Indlaeser timestamp fra en fil"""

    logging.info('Laeser tidstempel fra fil')
    return datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
    
def hent_matr_zip(ejerlav, outputfolder, updatetime):
    """Downloader zip filer fra atom feed"""

    ftp = ftplib.FTP('ftp.kortforsyningen.dk', config.BRUGERNAVN, config.PASSW)
    logging.info('Har forbindelse til kortforsynings ftp')

    ftp.cwd('atomfeeds/MATRIKELKORT/ATOM/SHAPE')

    tree = ET.parse(urllib.request.urlopen("http://download.kortforsyningen.dk/sites/default/files/feeds/MATRIKELKORT_SHAPE.xml"))
    entries = tree.findall('{http://www.w3.org/2005/Atom}entry')

    for node in entries:
        zipurl = node.find('{http://www.w3.org/2005/Atom}id').text
        updated = node.find('{http://www.w3.org/2005/Atom}updated').text
        dato = datetime.datetime.strptime(updated[:-6], '%Y-%m-%dT%H:%M:%S')
        print(dato)

    ftp.close()
    logging.info('Har lukket forbindelsen til ftp.')
    

if __name__ == '__main__':
    
    logging.basicConfig(filename='logfile.log', level=logging.DEBUG, filemode='w', format='%(asctime)s:%(levelname)s:%(message)s')

    last_update = read_lastupdate('logfile.log')

    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    hent_matr_zip(ejerlav, output_folder, last_update)

