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
import openerp.addons.decimal_precision as dp
from openerp import netsvc


class mrp_production(osv.osv):
    _inherit = "mrp.production"
    _columns ={
        'chicken': fields.boolean('Tracking Chickens', readonly=False, states={'done': [('readonly', True)]}),
        'remain_qty': fields.float('Remain Quantity', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'dead_ids': fields.one2many('dead.chickens.daily', 'mrp_id', 'Dead Chickens', readonly=False, states={'done': [('readonly', True)]}),
    }
    def create(self, cr, uid, vals, context=None):
        if vals.get('product_qty'):
            vals.update({'remain_qty': vals['product_qty']})
        return super(mrp_production, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None, update=False):
        if vals.get('product_qty'):
            vals.update({'remain_qty': vals['product_qty']})
        return super(mrp_production, self).write(cr, uid, ids, vals, context, update=False)

    def _make_production_internal_picking(self, cr, uid, mrp, move_ids, context=None):
        stock_picking = self.pool.get('stock.picking')
        stock_warehouse = self.pool.get('stock.warehouse')
        obj_data = self.pool.get('ir.model.data')
        int_type_id = False
        for move in move_ids:
            if not move.scrapped:
                location_id = move.location_id.usage == 'internal' and move.location_id.id or move.location_dest_id.id
                warehouse_ids = stock_warehouse.search(cr, uid, [('lot_stock_id','=', location_id)])
                if warehouse_ids:
                    warehouse = stock_warehouse.browse(cr, uid, warehouse_ids[0])
                    int_type_id = warehouse.int_type_id and warehouse.int_type_id.id or False
        picking_type_id = obj_data.get_object_reference(cr, uid, 'stock','picking_type_internal') and obj_data.get_object_reference(cr, uid, 'stock','picking_type_internal')[1] or False
        picking_id = stock_picking.create(cr, uid, {
                                                    'origin': mrp.name,
                                                    'picking_type_id': picking_type_id,
                                                    'move_type': 'direct',
                                                    'mrp_id': mrp.id,
                                                    'auto_picking': True,
                                                    'picking_type_id': int_type_id,
                                                }, context=context)
        return picking_id

    def action_confirm(self, cr, uid, ids, context=None):
        res = super(mrp_production, self).action_confirm(cr, uid, ids, context)
        for mrp in self.browse(cr, uid, ids, context):
            picking_id = self._make_production_internal_picking(cr, uid, mrp, mrp.move_lines, context)
            for move in mrp.move_lines:
                move.write({'picking_id': picking_id})
        return res

    def action_produce(self, cr, uid, production_id, production_qty, production_mode, wiz=False, context=None):
        if not context:
            context = {}
        res = super(mrp_production, self).action_produce(cr, uid, production_id, production_qty, production_mode, wiz, context)
        brw = self.browse(cr, uid, production_id, context=context)
        picking_id = self._make_production_internal_picking(cr, uid, brw, brw.move_created_ids2, context=context)
        old_stock_move_ids = [] #old finished goods
        for line in brw.move_created_ids2:
            if line.state != 'done' or line.location_dest_id.scrap_location: continue
            if not line.picking_id:
                line.write({'picking_id': picking_id}, context=context)
            else:
                old_stock_move_ids.append(line.id)

        #make entry
        stock_move_ids = [mv.id for mv in brw.move_lines2] #material in production
        self.pool.get('stock.picking').make_cost_price_journal_entry(cr, uid, [picking_id], dict(context, stock_move_ids=stock_move_ids, \
                                                                                                 old_stock_move_ids=old_stock_move_ids, \
                                                                                                 remain_qty = brw.remain_qty))
        brw.write({'remain_qty': brw.remain_qty-production_qty})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
