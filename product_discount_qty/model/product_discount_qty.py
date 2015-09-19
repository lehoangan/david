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

class product_discount_qty(osv.osv):
    _name = 'product.discount.qty'
    _inherit = ['mail.thread']

    _columns ={
        'type': fields.selection([('local', 'Local Market'),
                                  ('other', 'Other Market')], 'Market', required=True),
        'determine': fields.selection([('tag', 'Partner Tag'),
                                      ('saleman', 'Set Saleman Manually')], 'Condition of Market'),
        'qty': fields.float('For Each UoS(chicken)'),
        'disc_qty': fields.float('Disc KG'),
        'user_ids': fields.many2many('res.users', 'discount_qty_user_rel','disc_id', 'user_id', 'Saleman'),
        'partner_ids': fields.many2many('res.partner', 'discount_qty_partner_rel','disc_id', 'partner_id', 'Customer'),
        'product_ids': fields.many2many('product.product', 'discount_qty_product_rel','disc_id', 'product_id', 'Product'),
    }

    def onchange_type(self, cr, uid, ids, type):
        return {'value': {'determine': '',
                          'user_ids': []}}

    def write(self, cr, uid, ids, vals, context=None):
        message = '<span>%s</span>' % 'Other Tracking'
        self.message_post(cr, uid, ids, body=message, context=context)
        return super(product_discount_qty, self).write(cr, uid, ids, vals, context=context)

    def unlink(self, cr, uid, ids, context=None):
        model_pool = self.pool.get('ir.model')
        model_ids = model_pool.search(cr, uid, [('model', '=', self._name)])
        if model_ids:
            for id in ids:
                self.pool.get('history.delete').create(cr, uid, {'name': self.browse(cr, uid, id).type,
                                                                  'object_id': model_ids[0],
                                                                  'user_id': uid,
                                                                  'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                                                                  'res_id': id})
        return super(product_discount_qty, self).unlink(cr, uid, ids, context=context)





