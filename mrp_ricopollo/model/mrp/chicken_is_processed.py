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

class chicken_is_processed(osv.osv):
    _name = 'chicken.is.processed'
    _inherit = ['mail.thread']
    _columns ={
        'slaughtery_id': fields.many2one('slaughtery.chickens.daily', 'Número de Boleta', required=True),
        'date': fields.date('Date', required=True),
        'time': fields.float('Time'),
        'name': fields.char('Ref', 100, required=True),
        'warehouse_id': fields.many2one('stock.warehouse', 'Farm', required=True, domain=[('is_farm', '=', True)]),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'cycle_id': fields.many2one('history.cycle.form', 'Cycle', required=True, domain="[('warehouse_id','=', warehouse_id)]"),

        'qty_recibo': fields.float('Recibo Nro', required=True),
        'qty_buchis': fields.float('Total Kg', required=True),
        'qty_menudo': fields.float('Total Kg', required=True),
        'note': fields.text('Note'),
        'state': fields.selection([('draft', 'Draft'),
                                   ('confirm', 'Confirm'),
                                   ('cancel','Cancel')], 'State', readonly=True)
    }
    _order="date desc"
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
        }}

    def action_approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'confirm'}, context)
    
    def action_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'})

    def action_set_to_draft(self, cr, uid, ids, context):
        return self.write(cr, uid, ids, {'state': 'draft'})



 
