# -*- coding: utf-8 -*-

import base64
import json
from . import numbers_to_letterst
from . import request_api_sfs
from . import request_ftp_sfs

from odoo import models, fields, api

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
                                     ('12', 'enviado y aceptado sunat con obs.')], 'Estado D.E. SUNAT', default='01', copy = False)

    l10n_pe_edi_is_required = fields.Boolean(string="Is the Peruvian EDI needed", compute='_compute_l10n_pe_edi_is_required')
    l10n_pe_edi_cancel_cdr_number = fields.Char(copy=False, help="Reference from webservice to consult afterwards.")

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------

    @api.depends('move_type', 'company_id')
    def _compute_l10n_pe_edi_is_required(self):
        for move in self:
            move.l10n_pe_edi_is_required = move.country_code == 'PE' \
                and move.is_sale_document() and move.journal_id.l10n_latam_use_documents \
                and not move.l10n_pe_edi_cancel_cdr_number


    # -------------------------------------------------------------------------
    # SEQUENCE HACK
    # -------------------------------------------------------------------------
    def _get_last_sequence_domain(self, relaxed=False):
        # OVERRIDE
        where_string, param = super()._get_last_sequence_domain(relaxed)
        if self.l10n_pe_edi_is_required:
            where_string += " AND l10n_latam_document_type_id = %(l10n_latam_document_type_id)s"
            param['l10n_latam_document_type_id'] = self.l10n_latam_document_type_id.id or 0
        return where_string, param

    def _get_starting_sequence(self):
        # OVERRIDE
        if self.l10n_pe_edi_is_required and self.l10n_latam_document_type_id:
            doc_mapping = {'01': 'FFI', '03': 'BOL', '07': 'CNE', '08': 'NDI'}
            middle_code = doc_mapping.get(self.l10n_latam_document_type_id.code, self.journal_id.code)
            # TODO: maybe there is a better method for finding decent 2nd journal default invoice names
            if self.journal_id.code != 'INV':
                middle_code = middle_code[:1] + self.journal_id.code[:2]
            return "%s %s-00000000" % (self.l10n_latam_document_type_id.doc_code_prefix, middle_code)

        return super()._get_starting_sequence()

    #----------------------------------------------------------------
    #
    #----------------------------------------------------------------------

    def btn_test(self):
        _FTP_PARAM = self.company_id.l10n_pe_edi_sfs_ftp_server, self.company_id.l10n_pe_edi_sfs_ftp_user, self.company_id.l10n_pe_edi_sfs_ftp_pass
        print(_FTP_PARAM)


    def genera_doc_electronico(self):
        _RUC = self.company_id.vat
        _FTP_PARAM = self.company_id.l10n_pe_edi_sfs_ftp_server, self.company_id.l10n_pe_edi_sfs_ftp_user, self.company_id.l10n_pe_edi_sfs_ftp_pass
        _TIP_DOC = self.l10n_latam_document_type_id.code
        _SERIE_NUM = str(self.name).replace(' ', '')
        _NOM_JSON = _RUC+'-'+_TIP_DOC+'-'+_SERIE_NUM+'.json'

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
        # SI ES BOLETA DE VENTA '03' BORRAMOS CAMPOS DE PAGO
        if _TIP_DOC =='03':
            efactura.pop('datoPago', None)
            efactura.pop('detallePago', None)

        """ Envia .json en la Carpeta /DATA"""
        request_ftp_sfs.send_json_ftp(json.dumps(efactura, indent=2), _NOM_JSON, _FTP_PARAM)

        """Create attachment"""
        _json_b64 = base64.b64encode(json.dumps(efactura, indent=2).encode('utf-8'))
        self.create_attachment(_json_b64, _NOM_JSON)
        
        print('>>json generado')

        """GET API XML"""
        if self.sfs_ind_situ in ('01','05','06','10'):
            self.gen_xml()
            print('>>xml generado')

    def enviar_doc_electronico(self):

        if self.sfs_ind_situ in ('02', '05', '06', '07', '10'):
            self.send_xml()

    #   API Request
    def gen_xml(self):

        _IP_API = self.company_id.l10n_pe_edi_sfs_api
        _FTP_PARAM = self.company_id.l10n_pe_edi_sfs_ftp_server, self.company_id.l10n_pe_edi_sfs_ftp_user, self.company_id.l10n_pe_edi_sfs_ftp_pass
        _RUC = self.company_id.vat
        _TIP_DOC = self.l10n_latam_document_type_id.code
        _SERIE_NUM = str(self.name).replace(' ', '')

        print(_SERIE_NUM)
        """Genera Xml y actualiza sfs_id_situ"""
        _sfs_response = request_api_sfs.post_genera_xml(_RUC, _TIP_DOC, _SERIE_NUM,_IP_API)

        if _sfs_response['message'] != None or '':
            self.narration = _sfs_response['message']

        if _sfs_response['ind_situ'] != None:
            self.sfs_ind_situ = str(_sfs_response['ind_situ'])
        
        print('>>>> sfs_id_status = ', _sfs_response)
        
        _xml_b64 = None
        if self.sfs_ind_situ == '02':
            _xml_b64 = request_ftp_sfs.get_xml_ftp(f'{_RUC}-{_TIP_DOC}-{_SERIE_NUM}.xml', _FTP_PARAM)
            """Create atachment"""
            self.create_attachment(_xml_b64,f'{_RUC}-{_TIP_DOC}-{_SERIE_NUM}.xml')

            """get and update DigestValue"""
            _DigestValue = request_ftp_sfs.read_xml(f'{_RUC}-{_TIP_DOC}-{_SERIE_NUM}.xml')
            if _DigestValue!=None:
                self.DigestValue = _DigestValue


    def send_xml(self):
        _IP_API = self.company_id.l10n_pe_edi_sfs_api
        _FTP_PARAM = self.company_id.l10n_pe_edi_sfs_ftp_server, self.company_id.l10n_pe_edi_sfs_ftp_user, self.company_id.l10n_pe_edi_sfs_ftp_pass
        _RUC = self.company_id.vat
        _TIP_DOC = self.l10n_latam_document_type_id.code
        _SERIE_NUM = str(self.name).replace(' ', '')

        _sfs_response = request_api_sfs.post_envia_xml(_RUC, _TIP_DOC, _SERIE_NUM, _IP_API)

        if _sfs_response['message'] != None or '':
            self.narration = _sfs_response['message']

        if _sfs_response['ind_situ'] != None:
            self.sfs_ind_situ = str(_sfs_response['ind_situ'])

        print('>>Envio de DE a sunat =',_sfs_response)


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

        request_api_sfs.post_report_sfs(_RUC, _TIP_DOC, _SERIE_NUM)   

    @api.model
    def change_size_page_tk(self):
        print('Cambiar altura de papel')
        #paper_format = self.env['report.paperformat'].search([('name', '=', 'paperformat_ticket')])
        #for line in paper_format:
        #    print('>>papper format',line)
       
    def create_attachment(self,data_b64, name):

        #Buscar y eliminar si ya existe adjunto igual

        self.env['ir.attachment'].create({
            'name': name,
            'type': 'binary',
            'res_id': self.id,
            'res_model': 'account.move',
            'datas': data_b64,
            #'datas': base64.b64encode(file.encode('utf-8')),
            #'mimetype': 'application/json',
        })
