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
import time

class sale_order(osv.Model):

    _inherit = 'sale.order'
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'order_line' in vals:
            for order_id in ids:
                self._create_log_message(cr, uid, order_id, vals['order_line'], context)
        res = super(sale_order, self).write(cr, uid, ids, vals, context=context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        model_pool = self.pool.get('ir.model')
        model_ids = model_pool.search(cr, uid, [('model', '=', self._name)])
        if model_ids:
            for id in ids:
                self.pool.get('history.delete').create(cr, uid, {'name': self.browse(cr, uid, id).name,
                                                                  'object_id': model_ids[0],
                                                                  'user_id': uid,
                                                                  'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                                                                  'res_id': id})
        return super(sale_order, self).unlink(cr, uid, ids, context=context)

    def _create_log_message(self, cr, uid, order_id, data_lines, context=None):
        def format_message(message_description, tracked_values):
            message = ''
            if message_description:
                message = '<span>%s</span>' % message_description
            for name, change in tracked_values.items():
                message += '<div> &nbsp; &nbsp; &bull; <b>%s</b>: ' % change.get('col_info')
                if change.get('old_value'):
                    message += '%s &rarr; ' % change.get('old_value')
                message += '%s</div>' % change.get('new_value')
            return message
        dict_body = {}
        for line in data_lines:
            if not line or not line[2]: continue
            record =  self.pool.get('sale.order.line').browse(cr, uid, line[1])
            if 'price_unit' in line[2].keys():
                dict_body.update({'price_unit': {'new_value': line[2]['price_unit'], 'col_info': 'Unit Price', 'old_value': record.price_unit}})
            if 'quantity' in line[2].keys():
                dict_body.update({'quantity': {'new_value': line[2]['quantity'], 'col_info': 'Qty KG', 'old_value': record.quantity}})
            if 'product_uos_qty' in line[2].keys():
                dict_body.update({'product_uos_qty': {'new_value': line[2]['product_uos_qty'], 'col_info': 'Qty Unit', 'old_value': record.product_uos_qty}})
            if 'discount_kg' in line[2].keys():
                dict_body.update({'discount_kg': {'new_value': line[2]['discount_kg'], 'col_info': 'Discount KG', 'old_value': record.discount_kg}})
            if 'discount' in line[2].keys():
                dict_body.update({'discount': {'new_value': line[2]['discount'], 'col_info': 'Discount', 'old_value': record.discount}})
        message = format_message('Other Tracking', dict_body)
        if message:
            self.message_post(cr, uid, [order_id], body=message, context=context)
        return True

