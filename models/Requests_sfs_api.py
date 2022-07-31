import requests
import json

_IP_API = 'http://192.168.1.8:9000'
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

  response = requests.request("POST", _IP_API+_GENERA_XML, headers=headers, data=payload)
  parsed = json.loads(response.text)
  lst_ban_fac = parsed['listaBandejaFacturador']

  ind_situ = None
  if lst_ban_fac != None:
    disc_status = list(filter(lambda item: item['num_docu'] == num_docu and item['tip_docu'] == tip_docu, lst_ban_fac))
    for line in disc_status:
      ind_situ = line['ind_situ']
  return ind_situ

# Genera pdf en /REPO
def post_report_sfs(num_ruc, tip_docu, num_docu):
  payload = json.dumps({"nomArch": num_ruc+'-'+tip_docu+'-'+num_docu})
  headers = {'Content-Type': 'application/json'}
  response = requests.request("POST", _IP_API + _CREA_PDF, headers=headers, data=payload)
