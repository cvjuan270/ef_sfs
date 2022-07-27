# -*- coding: utf-8 -*-

import base64
import json
from odoo import models, fields
import requests_ftp
import Requests_sfs_api
import numbers_to_letterst


class AccountMove(models.Model):
    _inherit = 'account.move'

    DigestValue = fields.Char('Firma')
    sfs_ind_situ = fields.Selection([('01', 'por generar xml'),
                                     ('02', 'xml generado'),
                                     ('03', 'enviado y aceptado sunat'),
                                     ('04', 'enviado y aceptado sunat con obs.'),
                                     ('05', 'rechazado por sunat'),
                                     ('06', 'con errores'),
                                     ('07', 'por validar xml'),
                                     ('08', 'enviado a sunat por procesar'),
                                     ('09', 'enviado a sunat procesando'),
                                     ('10', 'rechazado por sunat'),
                                     ('11', 'enviado y aceptado sunat'),
                                     ('12', 'enviado y aceptado sunat con obs.')], 'situacion', default='01')

    def genera_doc_electronico(self):
        _RUC = self.company_id.vat
        _TIP_DOC = self.l10n_latam_document_type_id.code
        _SERIE_NUM = str(self.name).replace(' ', '')
        _NOM_JSON = _RUC+'-'+_TIP_DOC+'-'+_SERIE_NUM+'.json'
        print(_NOM_JSON)

        efactura = {
            'cabecera': self.get_cabecera_ft(),
            'adicionalCabecera': self.get_adicional_cabecera_ft(),
            'detalle': self.get_detalle_ft(),
            'tributos': self.get_trubutos_ft(self.get_cabecera_ft()['sumTotValVenta'], self.get_cabecera_ft()['sumTotTributos']),
            'leyendas': self.get_leyendas_ft(self.get_cabecera_ft()['sumImpVenta']),
            #'relacionados': '',
            #'adicionalCabecera': self.get_adicional_cabecera_ft(),
            'datoPago': self.get_datopago_ft(),
            'detallePago': self.get_detalle_pago(self.get_datopago_ft()['formaPago'])
        }
        # SI ES BOLETA DE VENTA '03' BORRAMOS CAMPOOS DE PAGO
        if _TIP_DOC =='03':
            efactura.pop('datoPago', None)
            efactura.pop('detallePago', None)
        print('>>>>>Genera .json')
        print('>>>>>Evia .json  /DATA')
        print(_NOM_JSON)
        requests_ftp.send_json_ftp(json.dumps(efactura, indent=2), _NOM_JSON)

        self.create_attachment(json.dumps(efactura, indent=2), _NOM_JSON, self.id)

    def get_cabecera_ft(self):
        cabecera = {
            # validar estado "draft":"borrador:
            'tipOperacion': '0101',
            'fecEmision': self.invoice_date.strftime('%Y-%m-%d'),
            'horEmision': self.invoice_date.strftime("%H:%M:%S"),
            'fecVencimiento': self.invoice_date_due.strftime('%Y-%m-%d'),
            'codLocalEmisor': '0000',
            'tipDocUsuario': self.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
            'numDocUsuario': self.partner_id.vat,
            'rznSocialUsuario': str(self.partner_id.name).strip(),
            'tipMoneda': self.currency_id.name,
            'sumTotTributos': str(round(self.amount_tax, 2)),
            'sumTotValVenta': str(round(self.amount_untaxed, 2)),
            'sumPrecioVenta': str(round(self.amount_total, 2)),
            'sumDescTotal': '0.00',
            'sumOtrosCargos': '0.00',
            'sumTotalAnticipos': '0.00',
            'sumImpVenta': str(round(self.amount_total, 2)),
            'ublVersionId': '2.1',
            'customizationId': '2.0',
            'adicionalCabecera': None
        }
        return cabecera

    def get_adicional_cabecera_ft(self):
        adicionalCabecera = []
        values = {
            "ctaBancoNacionDetraccion": "-",
            "codBienDetraccion": "-",
            "porDetraccion": "-",
            "mtoDetraccion": "-",
            "codMedioPago": "-",
            "codPaisCliente": "PE",
            "codUbigeoCliente": "-",
            "desDireccionCliente": "-",
            "codPaisEntrega": "-",
            "codUbigeoEntrega": "-",
            "desDireccionEntrega": "-"
        }
        adicionalCabecera.append(values)
        return adicionalCabecera

    def get_detalle_ft(self):
        detalle = []
        lines = []
        for ft in self:
           lines = ft.invoice_line_ids
        
        for line in lines:
            mtoValorUnitario = round(line.price_subtotal / line.quantity, 10)
            sumTotTributosItem = round(line.price_total - line.price_subtotal, 2)
            values = {
                'codUnidadMedida': 'ZZ',  # DEFINIR BIEN PARA ITEMS Y SERVICIOS
                'ctdUnidadItem': str(line.quantity),
                'codProducto': str(line.product_id.id),
                'codProductoSUNAT': '-',
                'desItem': line.product_id.name,
                'mtoValorUnitario': str(round(mtoValorUnitario, 6)),
                'sumTotTributosItem': str(round(sumTotTributosItem, 2)),
                'codTriIGV': '1000',
                'mtoIgvItem': str(round(sumTotTributosItem / line.quantity, 2)),
                'mtoBaseIgvItem': str(round(mtoValorUnitario, 2)),
                'nomTributoIgvItem': 'IGV',
                'codTipTributoIgvItem': 'VAT',
                'tipAfeIGV': '10',
                'porIgvItem': '18.00',
                'codTriISC': '-',
                'mtoIscItem': '0.00',
                'mtoBaseIscItem': '0.00',
                'nomTributoIscItem': '',
                'codTipTributoIscItem': '',
                'tipSisISC': '',
                'porIscItem': '0',
                'codTriOtro': '-',
                'mtoTriOtroItem': '0.00',
                'mtoBaseTriOtroItem': '0.00',
                'nomTributoOtroItem': 'OTROS',
                'codTipTributoOtroItem': 'OTH',
                'porTriOtroItem': '0',

                'codTriIcbper': '-',
                'mtoTriIcbperItem': '0.00',
                'ctdBolsasTriIcbperItem': '',
                'nomTributoIcbperItem': '',
                'codTipTributoIcbperItem': '',
                'mtoTriIcbperUnidad': '',
                'mtoPrecioVentaUnitario': str(round(line.price_total / line.quantity, 2)),
                'mtoValorVentaItem': str(round(line.price_subtotal, 2)),
                'mtoValorReferencialUnitario': '0.00',
            }
            detalle.append(values)
        return detalle
  
    def get_trubutos_ft(self, _mtoBaseImponible, _mtoTributo):
        lst = []
        values={
            'ideTributo': '1000',
            'nomTributo': 'IGV',
            'codTipTributo': 'VAT',
            'mtoBaseImponible': _mtoBaseImponible,
            'mtoTributo': _mtoTributo,
        }
        lst.append(values)
        return lst

    def get_leyendas_ft(self, totalventa):
        lst = []
        monto_letras = {
            'codLeyenda': '1000',
            'desLeyenda': numbers_to_letterst.numero_a_moneda_sunat(float(totalventa))
        }
        lst.append(monto_letras)
        return lst
    
    def get_relacionado_ft(self):
        
        lst = []
        values = {
            'indDocRelacionado': '',
            'numIdeAnticipo': '',
            'tipDocRelacionado': '',
            'numDocRelacionado': '',
            'tipDocEmisor': '',
            'numDocEmisor': '',
            'mtoDocRelacionado': ''
        }
        lst.append(values)
        return lst


    def get_datopago_ft(self):
        _formaPago = 'Credito'
        if self.invoice_date == self.invoice_date_due:
            _formaPago = 'Contado'

        values = {
            'formaPago': _formaPago,
            'mtoNetoPendientePago': str(round(self.amount_total, 2)),
            'tipMonedaMtoNetoPendientePago': 'PEN'
        }
        return values

    def get_detalle_pago(self,_formaPago):
        lst = []
        if _formaPago =='Credito':
            values = {
                'mtoCuotaPago': str(round(self.amount_total, 2)),
                'fecCuotaPago': self.invoice_date_due.strftime('%Y-%m-%d'),
                'tipMonedaCuotaPago': 'PEN'
            }
            lst.append(values)
        return lst

    def get_pdf_sfs(self):
        _RUC = self.company_id.vat
        _TIP_DOC = self.l10n_latam_document_type_id.code
        _SERIE_NUM = str(self.name).replace(' ', '')
        nombrejson = _RUC + '-' + _TIP_DOC + '-' + _SERIE_NUM + '.json'

        Requests_sfs_api.post_report_sfs(_RUC, _TIP_DOC, _SERIE_NUM)

    #   API Request
    def gen_xml(self):
        _RUC = self.company_id.vat
        _TIP_DOC = self.l10n_latam_document_type_id.code
        _SERIE_NUM = str(self.name).replace(' ', '')

        #    Actualiza bandeja antes de firmar xml
        Requests_sfs_api.post_actualiza()

        #   Genera Xml y actualiza sfs_id_situ
        print('>>>>post Firma xml')
        _sfs_id_situ = Requests_sfs_api.post_genera_xml(_RUC, _TIP_DOC, _SERIE_NUM)
        if _sfs_id_situ != None:
            self.sfs_ind_situ = str(_sfs_id_situ)
            print('>>>> sfs_id_status = ' + _sfs_id_situ)
        nomxml = _RUC+'-'+_TIP_DOC+'-'+_SERIE_NUM+'.xml'
        requests_ftp.get_xml_ftp(nomxml)


    def change_size_page_tk(self):
        print('Cambiar altura de papel')
        paper_format = self.env['report.paperformat']
        paper_format

        #paper_format.page_height = 300

    def create_attachment(self,jsonfile, name, id):
        self.env['ir.attachment'].create({
            'name': name,
            'type': 'binary',
            'res_id': self.id,
            'res_model': 'account.move',
            'datas': base64.b64encode(jsonfile.encode('utf-8')),
            'mimetype': 'application/json',
        })

# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class ef_sfs(models.Model):
#     _name = 'ef_sfs.ef_sfs'
#     _description = 'ef_sfs.ef_sfs'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100"""
