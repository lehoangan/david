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

class slaughtery_chickens_daily(osv.osv):
    _name = 'slaughtery.chickens.daily'
    _inherit = ['mail.thread']
    _columns ={
        'date': fields.date('Date', required=True),
        'time': fields.float('Time', required=True),
        'name': fields.char('Ref', 100, required=True),
        'warehouse_id': fields.many2one('stock.warehouse', 'From Farm', required=True, domain=[('is_farm', '=', True)]),
        'to_warehouse_id': fields.many2one('stock.warehouse', 'To Farm', domain=[('is_farm', '=', True)]),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'cycle_id': fields.many2one('history.cycle.form', 'Cycle', required=True, domain="[('warehouse_id','=', warehouse_id)]"),
        'picking_id': fields.many2one('stock.picking', 'Picking'),
        'qty_qq': fields.float('Total Pollos', required=True),
        'qty_kg': fields.float('Total Kg', required=True),
        'qty_dead': fields.float('Dead Chicken', required=True),
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

    def _get_default_farm(self, cr, uid, context):
        stock_warehouse = self.pool.get('stock.warehouse')
        warehouse_to_ids = stock_warehouse.search(cr, uid, [('code', '=', 'MAT1-FAEN')])
        if not warehouse_to_ids:
            return False

        return warehouse_to_ids[0]

    _defaults = {
        'date': lambda*a: time.strftime('%Y-%m-%d'),
        'state': 'draft',
        'product_id': _get_default_product,
        'to_warehouse_id': _get_default_farm,
     }

    def action_approve(self, cr, uid, ids, context=None):
        stock_picking = self.pool.get('stock.picking')
        stock_warehouse = self.pool.get('stock.warehouse')
        stock_move_obj = self.pool.get('stock.move')
        obj = self.browse(cr, uid, ids, context)[0]
        warehouse = obj.to_warehouse_id
        if not warehouse:
            warehouse_to_ids = stock_warehouse.search(cr, uid, [('code', '=', 'MAT1-FAEN')])
            if not warehouse_to_ids:
                openerp.exceptions.AccessError(_("Not find warehouse for MAT1-FAEN location"))

            warehouse = stock_warehouse.browse(cr, uid, warehouse_to_ids[0])
        int_type_id = warehouse.int_type_id and warehouse.int_type_id.id or False
        location_dest_id = warehouse.lot_stock_id.id

        picking_id = stock_picking.create(cr, uid, {
                                                    'origin': obj.name,
                                                    'move_type': 'direct',
                                                    'picking_type_id': int_type_id,
                                                }, context=context)
        stock_move = {
            'name': obj.name,
            'product_id': obj.product_id.id,
            # 'product_qty': obj.qty_qq,
            'product_uom_qty': obj.qty_qq,
            'location_id': obj.warehouse_id.lot_stock_id.id,
            'location_dest_id': location_dest_id,
            'picking_id': picking_id,
            'product_uom': obj.product_id.uom_id.id,
        }
        move_id = stock_move_obj.create(cr, uid, stock_move, context)
        stock_move_obj.action_assign(cr, uid, [move_id], context=context)
        stock_picking.action_done(cr, uid, [picking_id], context)
        stock_picking.make_cost_price_journal_entry(cr, uid, [picking_id], context)
        return self.write(cr, uid, ids, {'state': 'confirm',
                                         'picking_id': picking_id}, context)
    
    def action_cancel(self, cr, uid, ids, context=None):
        aml_obj = self.pool.get('account.move.line')
        am_objs = []
        for obj in self.browse(cr, uid, ids, context):
            if obj.picking_id:
                for move in obj.picking_id.move_lines:
                    aml_ids = aml_obj.search(cr, uid, [('stock_move_id', '=', move.id)])
                    if aml_ids:
                        for aml in aml_obj.browse(cr, uid, aml_ids):
                            if aml.move_id not in am_objs:
                                am_objs += [aml.move_id]
                obj.picking_id.action_revert_done()
                obj.picking_id.unlink()

        for am in am_objs:
            am.action_cancel()
        return self.write(cr, uid, ids, {'state': 'cancel'})

    def action_set_to_draft(self, cr, uid, ids, context):
        return self.write(cr, uid, ids, {'state': 'draft'})



 
