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

class mrp_request_form_line(osv.osv):
    _name = 'mrp.request.form.line'
    _columns ={
        'product_id': fields.many2one('product.product', 'Producto Solicitado', required=True),
        'request_id': fields.many2one('mrp.request.form', 'Parent', required=True,ondelete='cascade'),
        'qty_qq': fields.float('Quintales (qq)', required=True),
        'qty_unit': fields.float('Kilogramos', required=True),
        'uom_id': fields.many2one('product.uom', 'UoM', required=True),
    }

    def onchange_product_id(self, cr, uid, ids, product_id, qty_qq, context=None):
        if product_id:
            prod_obj = self.pool.get('product.product').browse(cr, uid, product_id, context)
            uom_id = prod_obj.uom_id.id
            qty_unit = qty_qq * 46
            return {'value': {'product_id': product_id,
                              'qty_qq': qty_qq,
                              'qty_unit': qty_unit,
                              'uom_id': uom_id}}
        return {'value': {'product_id': False,
                          'qty_qq': 0,
                          'qty_unit': 0,
                          'uom_id': False}}

 
