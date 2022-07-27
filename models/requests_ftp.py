#   Envia .json a la ruta /DATA del servidor SFS

_FTP_SERVER = '192.168.1.8'
_FTP_USER = 'Juan'
_FTP_PASS = '00Juan*897'

import os
import io
from ftplib import FTP
from xml.etree import ElementTree


def send_json_ftp(json, nombrejson):
    with FTP(_FTP_SERVER) as ftp:
        ftp.login(_FTP_USER, _FTP_PASS)
        bio = io.BytesIO()
        bio.write(json.encode())
        bio.seek(0)
        ftp.storbinary('STOR ' + 'DATA/' + nombrejson, bio)
        ftp.quit()

def get_xml_ftp(nombrexml):
    print(nombrexml)
    if os.path.exists(nombrexml):
        os.remove(f'{nombrexml}')

    ftp = FTP(_FTP_SERVER)
    ftp.login(_FTP_USER, _FTP_PASS)
    ftp.cwd('FIRMA')
    ftp.retrlines('LIST')
    ftp.retrbinary(f"RETR {nombrexml}", open(f'{nombrexml}', 'wb').write)

def read_xml(nombrexml):
    tree = ElementTree.parse(nombrexml)
    root = tree.getroot()
    DigestValue = ''
    for x in root.findall('.//{*}DigestValue'):
        DigestValue = x.text
    return DigestValue

if __name__ == "__main__":
    __main__()
    #get_xml_ftp('20604454558-03-B001-0014.xml')