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
import time

class daily_consumption_material(osv.osv):
    _name = 'daily.consumption.material'
    _columns ={
        'name': fields.char('Ref', 100),
        'product_id': fields.many2one('product.product', 'Material', required=True),
        'uom_id': fields.many2one('product.uom', 'UoM', required=True),
        'quantity': fields.float('Quantity'),
        'consumption_id': fields.many2one('daily.consumption', 'Consumption', required=True, ondelete="cascade"),
    }

    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        if not product_id:
            return {'value': {'uom_id': False,'name': ''}}

        prod = self.pool.get('product.product').browse(cr, uid, product_id, context)
        return {'value': {'uom_id': prod.uom_id.id,'name': prod.name}}

class daily_consumption_dead(osv.osv):
    _name = 'daily.consumption.dead'

    def _end_balance(self, cursor, user, ids, name, attr, context=None):
        res = {}
        for obj in self.browse(cursor, user, ids, context=context):
            res[obj.id] = obj.male_qty + obj.female_qty
        return res

    _columns ={
        'name': fields.char('Ref', 100),
        'product_id': fields.many2one('product.product', 'Chicken', required=True),
        'uom_id': fields.many2one('product.uom', 'UoM', required=True),
        'male_qty': fields.float('Macho Qty'),
        'female_qty': fields.float('Hembra Qty'),
        'total_qty': fields.function(_end_balance,
            store = {
                'daily.consumption.dead': (lambda self, cr, uid, ids, c={}: ids, ['male_qty','female_qty'], 10),
            },
            string="Total Qty"),
        'consumption_id': fields.many2one('daily.consumption', 'Consumption', required=True, ondelete="cascade"),
    }
    _defaults= {
        'type': 'mixed',
    }

    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        if not product_id:
            return {'value': {'uom_id': False}}

        uom_id = self.pool.get('product.product').browse(cr, uid, product_id, context).uom_id.id
        return {'value': {'uom_id': uom_id}}

    def onchange_qty(self, cr, uid, ids, male_qty, female_qty, context=None):
        total = male_qty + female_qty
        return {'value': {'total_qty': total}}

