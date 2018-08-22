import os
import time
import datetime

cur_folder = os.getcwd()
last_update = cur_folder + os.sep + "MatrikelDownload.log"

tid = time.mktime((2014, 8, 24, 18, 0, 0, 0, 0, 1))

def get_timestamp(filename):
    """
    Henter timestamp fra en fil
    """

    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

def set_timestamp(filename, date):
    """Aendrer timestamp paa en given fil"""

    os.utime(filename, (date, date))

if __name__ == '__main__':
    set_timestamp(last_update, tid)
    print(get_timestamp(last_update))
    
    
