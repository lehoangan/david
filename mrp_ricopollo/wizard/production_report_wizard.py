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

from openerp.osv import osv,fields
from openerp.tools.translate import _

class production_report_wizard(osv.osv_memory):

    _name = "production.report.wizard"

    _columns = {
        'warehouse_id': fields.many2one('stock.warehouse', 'Granja'),
        'cycle_id': fields.many2one('history.cycle.form', 'Lote'),
        'date_from': fields.date('Desde'),
        'date_to': fields.date('Hasta'),
        'food_type_id': fields.many2one('product.product', 'Tipo de Alimento', domain=[('food_type', '=', True)]),
        'product_id': fields.many2one('product.product', 'Producto', domain="[('bom_ids','!=',False),('bom_ids.type','!=','phantom')]"),
        'state': fields.selection([
            ('draft', 'Consolidated'),
            ('done', 'Completo'),
            ], 'Tipo de Reporte'),
        'report': fields.selection([
            ('product', 'Product report'),
            ('food', 'Type of Food report'),
            ('cycle', 'Per Cycle'),
            ], 'Tipo de Reporte'),
    }
    _defaults = {
        'state': 'draft',
        'report': 'product',
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['form'] = self.read(cr, uid, ids, [])[0]
        return self.pool['report'].get_action(cr, uid, [], 'production_report', data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

