from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_pe_edi_sfs_api = fields.Char('Url api', help='http://192.168.8.105:9000')
    l10n_pe_edi_sfs_ftp_server = fields.Char('ftp url/ip')
    l10n_pe_edi_sfs_ftp_user = fields.Char('ftp User')
    l10n_pe_edi_sfs_ftp_pass = fields.Char('ftp pass')
