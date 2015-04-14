# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv

class sale_sumary_report(osv.osv_memory):
    _name = "sale.sumary.report"

    _columns = {
        'date_from': fields.date('Desde'),
        'date_to': fields.date('Hasta'),
        'product_ids': fields.many2many('product.product', 'report_sale_product',
                                        'sale_id', 'product_id', 'Product',
                                        domain=[('sale_ok', '=', True)]),
        'state': fields.selection([
            ('draft', 'Presupuesto'),
            ('done', ' Orden de Venta'),
            ], 'Tipo'),
        'invoice_state': fields.selection([
            ('draft', 'Factura Borrador'),
            ('done', ' Factura'),
            ], 'Factura Tipo'),
    }
    _defaults={
    'state': 'done',
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['form'] = self.read(cr, uid, ids, ['date_from', 'date_to', 'state', 'product_ids','invoice_state'])[0]
        return self.pool['report'].get_action(cr, uid, [], 'sale_sumary_report', data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
