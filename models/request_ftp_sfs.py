import base64
import ftplib as FTP
import io
import os

#_FTP_SERVER = '192.168.1.8'
#_FTP_USER = 'Juan'
#_FTP_PASS = '00Juan*897'

#_FTP_SERVER = '192.168.8.105'
#_FTP_USER = 'juan'
#_FTP_PASS = '1308'

from ftplib import FTP
from xml.etree import ElementTree


def send_json_ftp(json, nombrejson, _FTP_PARAM):
    
    with FTP(str(_FTP_PARAM[0])) as ftp:
        ftp.login(str(_FTP_PARAM[1]), str(_FTP_PARAM[2]))
        bio = io.BytesIO()
        bio.write(json.encode())
        bio.seek(0)
        ftp.storbinary('STOR ' + 'DATA/' + nombrejson, bio)
        ftp.quit()

def get_xml_ftp(nombrexml, _FTP_PARAM):
    xml_file = f'/var/tmp/{nombrexml}'

    """if file exist => delete"""
    if os.path.exists(xml_file):
        os.remove(f'{xml_file}')

    ftp = FTP(str(_FTP_PARAM[0]))
    ftp.login(str(_FTP_PARAM[1]), str(_FTP_PARAM[2]))

    """cd to directorio"""
    ftp.cwd('FIRMA')
    #ftp.retrlines('LIST')
    ftp.retrbinary(f"RETR {nombrexml}", open(xml_file, 'wb').write)

    """Return xml"""
    with open(xml_file, 'rb') as file:
        xml_encode = base64.encodebytes(file.read()).decode('ISO-8859-1')
        return xml_encode

def read_xml(nombrexml):
    tree = ElementTree.parse(f'/var/tmp/{nombrexml}')
    root = tree.getroot()
    DigestValue = ''
    for x in root.findall('.//{*}DigestValue'):
        DigestValue = x.text
    return DigestValue

if __name__ == "__main__":
    __main__()