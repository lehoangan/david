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
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time

class dead_chickens_daily(osv.osv):
    _name = 'dead.chickens.daily'
    _columns ={
        'date': fields.date('Date', required=True),
        'mrp_id': fields.many2one('mrp.production', 'MO', required=True,ondelete='cascade'),
        'stock_move_id': fields.many2one('stock.move', 'Scrap Move', ondelete='cascade'),
        'quantity': fields.float('Quintales', required=True),
        'state': fields.selection([('draft', 'Draft'),
                                   ('confirm', 'Confirm'),
                                   ('cancel','Cancel')], 'State', readonly=True)
    }
    _defaults = {
                 'date': lambda*a : time.strftime('%Y-%m-%d'),
                 'state': 'draft'
                 }
    
    
    def action_confirm(self, cr, uid, ids, context=None):
        stock_mov_obj = self.pool.get('stock.move')
        location_obj = self.pool.get('stock.location')
        scrap_location_id = location_obj.search(cr, uid, [('scrap_location','=',True)])
        for obj in self.browse(cr, uid, ids, context):
            for move in obj.mrp_id.move_created_ids:
                extra_move_ids = stock_mov_obj.action_scrap(cr, uid, [move.id], obj.quantity, scrap_location_id[0],
                                                            restrict_lot_id=False,
                                                            restrict_partner_id=False, context=context)
                rm_qty = move.product_qty - obj.quantity
                if rm_qty < 0:
                    raise Warning(_('Deads quantity must be less than.'%move.product_qty))
                stock_mov_obj.write(cr, uid, extra_move_ids, {'production_id': obj.mrp_id.id, 'dead_chicken': True})
                move.write({'product_uom_qty': rm_qty})
                obj.write({'stock_move_id': extra_move_ids[0]})
                obj.mrp_id.write({'remain_qty': rm_qty})
                
        return self.write(cr, uid, ids, {'state': 'confirm'})
    
    def action_cancel(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            if obj.stock_move_id:
                for move in obj.mrp_id.move_created_ids:
                    rm_qty = move.product_qty + obj.quantity
                    obj.mrp_id.write({'remain_qty': rm_qty})
                    move.write({'product_uom_qty': rm_qty})
                obj.stock_move_id.write({'state': 'cancel'})
        return self.write(cr, uid, ids, {'state': 'cancel'})



 
