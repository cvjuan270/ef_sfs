from email import message
import json
import requests

_IP_API = 'http://192.168.8.105:9000'
_LIMPIAR = '/api/EliminarBandeja.htm'
_ACTUALIZAR = '/api/ActualizarPantalla.htm'
_GENERA_XML = '/api/GenerarComprobante.htm'
_ENVIA_SUNAT = '/api/enviarXML.htm'
_CREA_PDF = '/api/MostrarXml.htm'

def post_actualiza():
    payload = json.dumps({"txtSecuencia": "000"})
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", _IP_API+_ACTUALIZAR, headers=headers, data=payload)

# Genera y firma xml
def post_genera_xml(num_ruc, tip_docu, num_docu):

    payload = json.dumps({
        "num_ruc": str(num_ruc),
        "tip_docu": str(tip_docu),
        "num_docu": str(num_docu)
    })
    headers = {'Content-Type': 'application/json'}
    
    print(payload)
    response = requests.request("POST", _IP_API+_GENERA_XML, headers=headers, data=payload)
    parsed = json.loads(response.text)
    lst_ban_fac = parsed['listaBandejaFacturador']
    sfs_response = {'ind_situ': None, 'message': None}
    
    sfs_response['message'] = parsed['mensaje']

    if lst_ban_fac != None:
        disc_status = list(filter(lambda item: item['num_docu'] == num_docu and item['tip_docu'] == tip_docu, lst_ban_fac))
        for line in disc_status:
            sfs_response['ind_situ'] = line['ind_situ']


    return sfs_response

# Genera pdf en /REPO
def post_report_sfs(num_ruc, tip_docu, num_docu):
    payload = json.dumps({"nomArch": num_ruc+'-'+tip_docu+'-'+num_docu})
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", _IP_API + _CREA_PDF, headers=headers, data=payload)

if __name__ == "__main__":
    __main__()