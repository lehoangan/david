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

    def _make_production_internal_picking(self, cr, uid, mrp, context=None):
        stock_picking = self.pool.get('stock.picking')
        obj_data = self.pool.get('ir.model.data')
        picking_type_id = obj_data.get_object_reference(cr, uid, 'stock','picking_type_internal') and obj_data.get_object_reference(cr, uid, 'stock','picking_type_internal')[1] or False
        picking_id = stock_picking.create(cr, uid, {
                                                    'origin': mrp.name,
                                                    'picking_type_id': picking_type_id,
                                                    'move_type': 'direct',
                                                    'mrp_id': mrp.id,
                                                    'auto_picking': True,
                                                }, context=context)
        return picking_id

    def action_confirm(self, cr, uid, ids, context=None):
        res = super(mrp_production, self).action_confirm(cr, uid, ids, context)
        for mrp in self.browse(cr, uid, ids, context):
            picking_id = self._make_production_internal_picking(cr, uid, mrp, context)
            for move in mrp.move_lines:
                move.write({'picking_id': picking_id})
        return res

    def action_produce(self, cr, uid, production_id, production_qty, production_mode, wiz=False, context=None):
        if not context:
            context = {}
        res = super(mrp_production, self).action_produce(cr, uid, production_id, production_qty, production_mode, wiz, context)
        brw = self.browse(cr, uid, production_id, context=context)
        picking_id = self._make_production_internal_picking(cr, uid, brw, context=context)
        old_stock_move_ids = []
        for line in brw.move_created_ids2:
            if not line.picking_id:
                line.write({'picking_id': picking_id}, context=context)
            else:
                old_stock_move_ids.append(line.id)

        #make entry
        stock_move_ids = [mv.id for mv in brw.move_lines2]
        dict_material = {}
        if brw.state != 'done':
            bom_obj = self.pool.get('mrp.bom')
            uom_obj = self.pool.get('product.uom')
            # get components and workcenter_lines from BoM structure
            factor = uom_obj._compute_qty(cr, uid, brw.product_uom.id, production_qty, brw.bom_id.product_uom.id)
            # product_lines, workcenter_lines
            results, results2 = bom_obj._bom_explode(cr, uid, brw.bom_id, brw.product_id, factor / brw.bom_id.product_qty, {}, routing_id=brw.routing_id.id, context=context)

            # reset product_lines in production order
            for line in results:
                print line
                dict_material.update({line['product_id']: line['product_qty']})
        self.pool.get('stock.picking').make_cost_price_journal_entry(cr, uid, [picking_id], dict(context, stock_move_ids=stock_move_ids, \
                                                                                                 old_stock_move_ids=old_stock_move_ids, \
                                                                                                 produce_qty = production_qty, \
                                                                                                 dict_material = dict_material))
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
