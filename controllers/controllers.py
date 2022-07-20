# -*- coding: utf-8 -*-
# from odoo import http


# class EfSfs(http.Controller):
#     @http.route('/ef_sfs/ef_sfs', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ef_sfs/ef_sfs/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ef_sfs.listing', {
#             'root': '/ef_sfs/ef_sfs',
#             'objects': http.request.env['ef_sfs.ef_sfs'].search([]),
#         })

#     @http.route('/ef_sfs/ef_sfs/objects/<model("ef_sfs.ef_sfs"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ef_sfs.object', {
#             'object': obj
#         })
