# -*- coding: utf-8 -*-

import datetime
import json
from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

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

    @api.depends()
    def get_partner(self):
        cabecera = {
            # validar estado "draft":"borrador:
            'fecEmision': self.invoice_date.strftime('%Y-%m-%d'),
            'horEmision': self.invoice_date.strftime("%H:%M:%S"),
            'fecVencimiento': self.invoice_date_due.strftime('%Y-%m-%d'),
            'tipDocUsuario': self.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
            'numDocUsuario': self.partner_id.vat,
            'rznSocialUsuario': self.partner_id.name,
            'tipMoneda': self.currency_id.name,
            'sumTotTributos': str(round(self.amount_tax, 2)),
            'sumTotValVenta': str(round(self.amount_untaxed, 2)),
            'sumPrecioVenta': str(round(self.amount_total, 2)),
            'sumDescTotal': '0.00',
            'sumOtrosCargos': '0.00',
            'sumTotalAnticipos': '0.00',
            'sumImpVenta': str(round(self.amount_total, 2))
        }

        print(json.dumps(cabecera, indent=3))

    """@api.depends('invoice_date', 'create_date', 'invoice_date_due', 'partner_id')
    def get_partner_(self):

        for am in self:
            cabecera = {
                # validar estado "draft":"borrador:
                'fecEmision': am.invoice_date.strftime('%Y-%m-%d'),
                'horEmision': am.invoice_date.strftime("%H:%M:%S"),
                'fecVencimiento': am.invoice_date_due.strftime('%Y-%m-%d'),
                'tipDocUsuario': am.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
                'numDocUsuario': am.partner_id.vat,
                'rznSocialUsuario': am.partner_id.name,
                'tipMoneda': am.currency_id.name,
                'sumTotTributos': str(round(am.amount_tax, 2)),
                'sumTotValVenta': str(round(am.amount_untaxed, 2)),
                'sumPrecioVenta': str(round(am.amount_total, 2)),
                'sumDescTotal': '0.00',
                'sumOtrosCargos': '0.00',
                'sumTotalAnticipos': '0.00',
                'sumImpVenta': str(round(am.amount_total, 2))
            }
            
            lines = am.invoice_line_ids
            det = []
            for line in lines:
                _detalle = f_detalle()
                _detalle.codUnidadMedida = line.product_id.type #DEFINIR BIEN PARA ITEMS Y SERVICIOS
                _detalle.ctdUnidadItem = abs(line.quantity)
                _detalle.codProducto = str(line.product_id.id)
                _detalle.codProductoSUNAT = ''
                _detalle.desItem = line.product_id.name
                mtoValorUnitario = round(line.price_subtotal / line.quantity, 10)
                _detalle.mtoValorUnitario = str(mtoValorUnitario)
                _detalle.mtoValorUnitario = str(round(line.price_subtotal/line.quantity, 10))
                sumTotTributosItem = round(line.price_total-line.price_subtotal, 2)
                _detalle.sumTotTributosItem = str(sumTotTributosItem)
                _detalle.codTriIGV = '1000'
                _detalle.mtoIgvItem = str(sumTotTributosItem/line.quantity)
                _detalle.mtoBaseIgvItem = str(round(mtoValorUnitario, 2))
                _detalle.nomTributoIgvItem = 'IGV'
                _detalle.codTipTributoIgvItem = 'VAT'
                _detalle.tipAfeIGV = '1000'
                _detalle.porIgvItem = '18.00'
                _detalle.codTriISC = '2000'
                _detalle.mtoIscItem = '0.00'
                _detalle.mtoBaseIscItem = '0.00'
                _detalle.nomTributoIscItem = 'ISC'
                _detalle.codTipTributoIscItem = 'EXC'
                _detalle.tipSisISC = '01'
                _detalle.porIscItem = '15.00'
                _detalle.codTriOtro = '-'
                _detalle.mtoTriOtroItem = '0.00'
                _detalle.mtoBaseTriOtroItem = '0.00'
                _detalle.nomTributoOtroItem = 'OTROS'
                _detalle.codTipTributoOtroItem = 'OTH'
                _detalle.porTriOtroItem = '15.00'
                
                _detalle.codTriIcbper = '-'
                _detalle.mtoTriIcbperItem = '0.00'
                _detalle.ctdBolsasTriIcbperItem = '0.00'
                _detalle.nomTributoIcbperItem = 'ICBPER'
                _detalle.codTipTributoIcbperItem = 'OTH'
                _detalle.mtoTriIcbperUnidad = '0.00'
                _detalle.mtoPrecioVentaUnitario = str(round(line.price_total/line.quantity))
                _detalle.mtoValorVentaItem = str(mtoValorUnitario)
                _detalle.mtoValorReferencialUnitario = '-'

                det.append(_detalle.__dict__)
            efactura.detalle = det
            print(json.dumps(efactura, indent=3))
        #print(json.dums(efactura.__dict__, indent=3))
            #print(json.dumps(_detalle.__dict__, indent=3))
            #print(am.partner_id.name)
            #print(json.dumps(_cabecera.__dict__, indent=3))
            #partner1 = self.env['res.partner'].browse([am.partner_id])
            #print(partner1.name)
#objects
class f_cabecera:
    def __init__(self):
        self.tipOperacion='0101'
        self.fecEmision = ''
        self.horEmision = ''
        self.fecVencimiento = ''
        self.codLocalEmisor = '0000'
        self.tipDocUsuario = ''
        self.numDocUsuario = ''
        self.rznSocialUsuario = ''
        self.tipMoneda = 'PEN'
        self.sumTotTributos = ''
        self.sumTotValVenta = ''
        self.sumPrecioVenta = ''
        self.sumDescTotal = ''
        self.sumOtrosCargos = ''
        self.sumTotalAnticipos = ''
        self.sumImpVenta = ''
        self.ublVersionId = '2.1'
        self.customizationId = '2.0'

class f_detalle:
    def __init__(self):
        self.codUnidadMedida = ''
        self.ctdUnidadItem = ''
        self.codProducto = ''
        self.codProductoSUNAT = ''
        self.desItem = ''
        self.mtoValorUnitario = ''
        self.sumTotTributosItem = ''
        self.codTriIGV = ''
        self.mtoIgvItem = ''
        self.mtoBaseIgvItem = ''
        self.nomTributoIgvItem = ''
        self.codTipTributoIgvItem = ''
        self.tipAfeIGV = ''
        self.porIgvItem = ''
        self.codTriISC = ''
        self.mtoIscItem = ''
        self.mtoBaseIscItem = ''
        self.nomTributoIscItem = ''
        self.codTipTributoIscItem = ''
        self.tipSisISC = ''
        self.porIscItem = ''
        self.codTriOtro = ''
        self.mtoTriOtroItem = ''
        self.mtoBaseTriOtroItem = ''
        self.nomTributoOtroItem = ''
        self.codTipTributoOtroItem = ''
        self.porTriOtroItem = ''
        self.codTriIcbper = ''
        self.mtoTriIcbperItem = ''
        self.ctdBolsasTriIcbperItem = ''
        self.nomTributoIcbperItem = ''
        self.codTipTributoIcbperItem = ''
        self.mtoTriIcbperUnidad = ''
        self.mtoPrecioVentaUnitario = ''
        self.mtoValorVentaItem = ''
        self.mtoValorReferencialUnitario = ''

class f_tributos:
    def __init__(self):
        self.ideTributo = ''
        self.nomTributo = ''
        self.codTipTributo = ''
        self.mtoBaseImponible = ''
        self.mtoTributo = ''

class f_leyendas:
    def __init__(self) -> None:
        self.codLeyenda = ''
        self.desLeyenda = ''

class f_relacionados:
    def __init__(self):
        self.indDocRelacionado = ''
        self.numIdeAnticipo = ''
        self.tipDocRelacionado = ''
        self.numDocRelacionado = ''
        self.tipDocEmisor = ''
        self.numDocEmisor = ''
        self.mtoDocRelacionado = ''

class f_adicionalcabecera:
    def __init__(self) -> None:
        self.ctaBancoNacionDetraccion = ''
        self.codBienDetraccion = ''
        self.porDetraccion = ''
        self.mtoDetraccion = ''
        self.codMedioPago = ''
        self.codPaisCliente = ''
        self.codUbigeoCliente = ''
        self.desDireccionCliente = ''
        self.codPaisEntrega = ''
        self.codUbigeoEntrega = ''
        self.desDireccionEntrega = ''

class f_datoPago:
    def __init__(self):
        self.formaPago = ''
        self.mtoNetoPendientePago = ''
        self.tipMonedaMtoNetoPendientePago = ''

class f_detallePago:
    def __init__(self) -> None:
        self.mtoCuotaPago = ''
        self.fecCuotaPago = ''
        self.tipMonedaCuotaPago = ''

#instan
_cabecera = f_cabecera()
#_detalle = f_detalle()
_tributos = f_tributos()
_leyendas = f_leyendas()
_relacionados = f_relacionados()
_adicionalcabecera = f_adicionalcabecera()
_datoPago = f_datoPago()
_detallePago = f_detallePago()



efactura = {}
efactura['cabecera'] = _cabecera.__dict__
efactura['detalle'] = []
efactura['tributos'] =[]
efactura['leyendas'] = []
efactura['relacionados'] = []
efactura['adicionalCabecera'] = {}
efactura['datoPago'] ={}
efactura['detallePago'] = []

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
