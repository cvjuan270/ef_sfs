# -*- coding: utf-8 -*-

from email.policy import default
from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sfs_mot_traslado = fields.Selection([
        ('01', 'Venta'),
        ('02', 'Compra'),
        ('04', 'Traslado entre establecimientos de la misma empresa'),
        ('08', 'Importación'),
        ('09', 'Exportación'),
        ('13', 'Otros'),
        ('14', 'Venta sujeta a confirmación del comprador'),
        ('18', 'Traslado emisor itinerante CP'),
        ('19', 'Traslado a zona primaria'),
        ], 'Motivo de traslado', default='01', copy = False)

    def get_cabecera_gr(self):
        cabecera = {
            'fecEmision': self.schenduled_date.strftime('%Y-%m-%d'),
            'horEmision': self.schenduled_date.strftime("%H:%M:%S"),
            'tipDocGuia': '09',
            'serNumDocGuia': self.name,
            'numDocDestinatario': self.partner_id.vat,
            'tipDocDestinatario': self.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
            'rznSocialDestinatario': str(self.partner_id.name).strip(),
            'motTrasladoDatosEnvio': str(self.sfs_mot_traslado),
            'desMotivoTrasladoDatosEnvio': str(self.sfs_mot_traslado['name']),
            'indTransbordoProgDatosEnvio': 'false',
            'psoBrutoTotalBienesDatosEnvio': '0.0',
            'uniMedidaPesoBrutoDatosEnvio': 'KGM',
            'numBultosDatosEnvio': '',
            'modTrasladoDatosEnvio': '02',
            'fecInicioTrasladoDatosEnvio': self.schenduled_date.strftime('%Y-%m-%d'),
            'numDocTransportista': '',
            'tipDocTransportista': '',
            'nomTransportista': '',
            'numPlacaTransPrivado': 'V0M-298',
            'numDocIdeConductorTransPrivado': '44650206',
            'tipDocIdeConductorTransPrivado': '1',
            'nomConductorTransPrivado': 'Robinson Deyby Tito Vizcardo',
            'ubiLlegada': '010540',
            'dirLlegada': 'CAL. LOS ARCHIPIELAGOS MZA. C LOTE. 10C URB. LA CAPITANA',
            'ubiPartida': '040101',
            'dirPartida': 'PJ. SANTA CATALINA 2DO. PISO NRO. 106 AREQUIPA - AREQUIPA - AREQUIPA',
            'ublVersionId': '2.1',
            'customizationId': '1.0'
        }
        return cabecera