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

class final_part_of_product(osv.osv):
    _name = 'final.part.of.product'
    _inherit = ['mail.thread']
    _columns ={
        'slaughtery_id': fields.many2one('slaughtery.chickens.daily', 'Número de Boleta', required=True,
        readonly=True, states={'draft': [('readonly', False)]}),
        'date': fields.date('Date', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'name': fields.char('Nro. Recibo', 100, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'warehouse_id': fields.many2one('stock.warehouse', 'Farm', required=True, domain=[('is_farm', '=', True)],
        readonly=True, states={'draft': [('readonly', False)]}),
        'cycle_id': fields.many2one('history.cycle.form', 'Cycle', required=True, domain="[('warehouse_id','=', warehouse_id),('date_end', '=', False)]",
        readonly=True, states={'draft': [('readonly', False)]}),

        'line_used_ids': fields.one2many('final.part.of.product.used.detail', 'parent_used_id', 'Used Details',
        readonly=True, states={'draft': [('readonly', False)]}),

        'line_finish_ids': fields.one2many('final.part.of.product.finish.detail', 'parent_finish_id', 'Finish Details',
        readonly=True, states={'draft': [('readonly', False)]}),

        'note': fields.text('Note'),
        'state': fields.selection([('draft', 'Draft'),
                                   ('confirm', 'Confirm'),
                                   ('cancel','Cancel')], 'State', readonly=True)
    }
    _defaults = {
        'date': lambda*a: time.strftime('%Y-%m-%d'),
        'state': 'draft',
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
        }}

    def action_approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'confirm'}, context)
    
    def action_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'})

    def action_set_to_draft(self, cr, uid, ids, context):
        return self.write(cr, uid, ids, {'state': 'draft'})

class final_products_for_sale_used_detail(osv.osv):
    _name = 'final.part.of.product.used.detail'
    def _average_get(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res.update({obj.id: obj.weight/obj.qty })
        return res
    _columns={
        'product_id': fields.many2one('product.product', 'Productos', required=True),
        'parent_used_id': fields.many2one('final.part.of.product', 'Parent'),

        'qty': fields.float('Unit', required=True),
        'weight': fields.float('Weight', required=True),
        'average': fields.function(_average_get, string='Average weight', type='float'),
    }

    def onchange_qty(self, cr, uid, ids, qty, weight, context=None):
        if not qty or not weight:
            return {'value': {'average': 0}}

        return {'value': {'average': weight/qty}}


class final_products_for_sale_finish_detail(osv.osv):
    _name = 'final.part.of.product.finish.detail'

    def _average_get(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res.update({obj.id: obj.weight/obj.qty })
        return res

    _columns={
        'product_id': fields.many2one('product.product', 'Productos', required=True),
        'parent_finish_id': fields.many2one('final.part.of.product', 'Parent'),

        'qty': fields.float('Unit', required=True),
        'weight': fields.float('Weight', required=True),
        'average': fields.function(_average_get, string='Average weight', type='float'),

    }

    def onchange_qty(self, cr, uid, ids, qty, weight, context=None):
        if not qty or not weight:
            return {'value': {'average': 0}}

        return {'value': {'average': weight/qty}}

 
