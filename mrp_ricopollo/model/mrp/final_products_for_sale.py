# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.tools.translate import _
import openerp
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time

class final_products_for_sale(osv.osv):
    _name = 'final.products.for.sale'
    _inherit = ['mail.thread']
    _columns ={
        'slaughtery_id': fields.many2one('slaughtery.chickens.daily', 'Número de Boleta', required=True),
        'date': fields.date('Date', required=True),
        'name': fields.char('Ref', 100, required=True),
        'warehouse_id': fields.many2one('stock.warehouse', 'Farm', required=True, domain=[('is_farm', '=', True)]),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'cycle_id': fields.many2one('history.cycle.form', 'Cycle', required=True, domain="[('warehouse_id','=', warehouse_id)]"),

        'qty_descarte': fields.float('Pollo Descarte'),
        'qty_descarte_kg': fields.float('Pollo Descarte kg'),

        'qty_patas': fields.float('Patas kg'),
        'qty_patas_kg': fields.float('Patas descarte kg'),

        'qty_rojo': fields.float('Pollo Rojo'),
        'qty_rojo_kg': fields.float('Pollo Rojo Kg'),

        'qty_rotas_rojas': fields.float('Alas Rotas Rojas'),
        'qty_rotas_rojas_kg': fields.float('Alas Rotas Rojas Kg'),

        'qty_rotas_blancas': fields.float('Alas Rotas Blancas'),
        'qty_rotas_blancas_kg': fields.float('Alas Rotas Blancas Kg'),

        'qty_pernas_rotas': fields.float('Piernas Rotas'),
        'qty_pernas_rotas_kg': fields.float('Piernas Rotas Kg'),

        'qty_pernas_abiertas': fields.float('Piernas Abiertas'),
        'qty_pernas_abiertas_kg': fields.float('Piernas Abiertas Kg'),

        'qty_producto_para_embutidos': fields.float('Producto para embutidos Kg'),

        'line_ids': fields.one2many('final.products.for.sale.detail', 'parent_id', 'Details'),

        'note': fields.text('Note'),
        'state': fields.selection([('draft', 'Draft'),
                                   ('confirm', 'Confirm'),
                                   ('cancel','Cancel')], 'State', readonly=True)
    }
    def _get_default_product(self, cr, uid, context):
        product_ids = self.pool.get('product.product').search(cr, uid, [('name', '=', '102 Pollito BB')])
        if product_ids:
            return product_ids[0]
        return False

    _defaults = {
        'date': lambda*a: time.strftime('%Y-%m-%d'),
        'state': 'draft',
        'product_id': _get_default_product,
     }

    def onchange_slaughtery_id(self, cr, uid, ids, slaughtery_id, context={}):
        if not slaughtery_id:
            return {'value': {}}

        slaughtery = self.pool.get('slaughtery.chickens.daily').browse(cr, uid, slaughtery_id, context)

        return {'value': {
            'warehouse_id': slaughtery.warehouse_id.id,
            'cycle_id': slaughtery.cycle_id.id,
            'date': slaughtery.date,
            'name': slaughtery.name,
            'product_id': slaughtery.product_id and slaughtery.product_id.id or False,
        }}

    def action_approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'confirm'}, context)
    
    def action_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'})

    def action_set_to_draft(self, cr, uid, ids, context):
        return self.write(cr, uid, ids, {'state': 'draft'})

class final_products_for_sale_detail(osv.osv):
    _name = 'final.products.for.sale.detail'
    _columns={
        'product_id': fields.many2one('product.product', 'Cajas', required=True),
        'parent_id': fields.many2one('final.products.for.sale', 'Parent'),

        'qty': fields.float('Cantidad', required=True),
        'weight': fields.float('Peso Bruto', required=True),
    }

 
