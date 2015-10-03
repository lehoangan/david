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
import openerp.addons.decimal_precision as dp
import time

class product_pricelist_version(osv.osv):
    _name = "product.pricelist.version"
    _inherit = ['product.pricelist.version', 'mail.thread']

    _columns = {
        'items_id': fields.one2many('product.pricelist.item',
            'price_version_id', 'Price List Items', required=True, copy=True,track_visibility='onchange'),
        'date_start': fields.date('Start Date', help="First valid date for the version.",track_visibility='onchange'),
        'date_end': fields.date('End Date', help="Last valid date for the version.",track_visibility='onchange'),
    }

    def write(self, cr, uid, ids, vals, context=None):
        if 'items_id' in vals:
            for order_id in ids:
                self._create_log_message(cr, uid, order_id, vals['items_id'], context)
        res = super(product_pricelist_version, self).write(cr, uid, ids, vals, context=context)
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
        return super(product_pricelist_version, self).unlink(cr, uid, ids, context=context)

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
            record =  self.pool.get('product.pricelist.item').browse(cr, uid, line[1])
            dict_body.update({'name': {'new_value': record.name, 'col_info': 'Rule', 'old_value': ''}})
            if 'min_quantity' in line[2].keys():
                dict_body.update({'min_quantity': {'new_value': line[2]['min_quantity'], 'col_info': 'Min Qty', 'old_value': record.min_quantity}})
            if 'price_surcharge' in line[2].keys():
                dict_body.update({'price_surcharge': {'new_value': line[2]['price_surcharge'], 'col_info': 'Price Surcharge', 'old_value': record.price_surcharge}})
            if 'product_id' in line[2].keys():
                product = ''
                if line[2]['product_id']:
                    product = self.pool.get('product.product').browse(cr, uid, line[2]['product_id']).name
                dict_body.update({'product_id': {'new_value': product, 'col_info': 'Product', 'old_value': record.product_id and record.product_id.name or ''}})
            if 'categ_id' in line[2].keys():
                product = ''
                if line[2]['categ_id']:
                    product = self.pool.get('product.category').browse(cr, uid, line[2]['categ_id']).name
                dict_body.update({'categ_id': {'new_value': product, 'col_info': 'Product Category', 'old_value': record.categ_id and record.categ_id.name or ''}})
            if 'price_discount' in line[2].keys():
                dict_body.update({'price_discount': {'new_value': line[2]['price_discount'], 'col_info': 'Price Surcharge', 'old_value': record.price_discount}})
            if 'price_round' in line[2].keys():
                dict_body.update({'price_round': {'new_value': line[2]['price_round'], 'col_info': 'Price Discount', 'old_value': record.price_round}})
            if 'price_min_margin' in line[2].keys():
                dict_body.update({'price_min_margin': {'new_value': line[2]['price_min_margin'], 'col_info': 'Min. Price Margin', 'old_value': record.price_min_margin}})
            if 'price_max_margin' in line[2].keys():
                dict_body.update({'price_max_margin': {'new_value': line[2]['price_max_margin'], 'col_info': 'Max. Price Margin', 'old_value': record.price_max_margin}})
        message = format_message('Other Tracking:', dict_body)
        if message:
            self.message_post(cr, uid, [order_id], body=message, context=context)
        return True

class product_pricelist_item(osv.osv):
    _name = "product.pricelist.item"
    _inherit = ['product.pricelist.item', 'mail.thread']

    _columns = {
        'product_id': fields.many2one('product.product', 'Product', ondelete='cascade',track_visibility='onchange', help="Specify a product if this rule only applies to one product. Keep empty otherwise."),
        'categ_id': fields.many2one('product.category', 'Product Category', ondelete='cascade',track_visibility='onchange', help="Specify a product category if this rule only applies to products belonging to this category or its children categories. Keep empty otherwise."),
        'min_quantity': fields.integer('Min. Quantity', required=True,track_visibility='onchange',
            help="For the rule to apply, bought/sold quantity must be greater "
              "than or equal to the minimum quantity specified in this field.\n"
              "Expressed in the default UoM of the product."
            ),

        'price_surcharge': fields.float('Price Surcharge',track_visibility='onchange',
            digits_compute= dp.get_precision('Product Price'), help='Specify the fixed amount to add or substract(if negative) to the amount calculated with the discount.'),
        'price_discount': fields.float('Price Discount', digits=(16,4),track_visibility='onchange'),
        'price_round': fields.float('Price Rounding',track_visibility='onchange',
            digits_compute= dp.get_precision('Product Price'),
            help="Sets the price so that it is a multiple of this value.\n" \
              "Rounding is applied after the discount and before the surcharge.\n" \
              "To have prices that end in 9.99, set rounding 10, surcharge -0.01" \
            ),
        'price_min_margin': fields.float('Min. Price Margin',track_visibility='onchange',
            digits_compute= dp.get_precision('Product Price'), help='Specify the minimum amount of margin over the base price.'),
        'price_max_margin': fields.float('Max. Price Margin',track_visibility='onchange',
            digits_compute= dp.get_precision('Product Price'), help='Specify the maximum amount of margin over the base price.'),
    }

    def unlink(self, cr, uid, ids, context=None):
        model_pool = self.pool.get('ir.model')
        model_ids = model_pool.search(cr, uid, [('model', '=', self._name)])
        if model_ids:
            for id in ids:
                obj = self.browse(cr, uid, id)
                pricelist = obj.price_version_id and obj.price_version_id.pricelist_id and obj.price_version_id.pricelist_id.name or ''
                version = obj.price_version_id and obj.price_version_id.name or ''
                self.pool.get('history.delete').create(cr, uid, {'name': '%s - %s - %s'%(pricelist, version, obj.name),
                                                                  'object_id': model_ids[0],
                                                                  'user_id': uid,
                                                                  'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                                                                  'res_id': id})
        return super(product_pricelist_item, self).unlink(cr, uid, ids, context=context)

class product_template(osv.Model):
    _inherit = 'product.template'

    _columns = {
        'sale_ok': fields.boolean('Can be Sold', help="Specify if the product can be selected in a sales order line.",track_visibility='onchange'),
        'uom_id': fields.many2one('product.uom', 'Unit of Measure', required=True, help="Default Unit of Measure used for all stock operation.",track_visibility='onchange'),
        'list_price': fields.float('Sale Price', digits_compute=dp.get_precision('Product Price'), help="Base price to compute the customer price. Sometimes called the catalog price.",track_visibility='onchange'),
        'standard_price': fields.property(type = 'float', digits_compute=dp.get_precision('Product Price'),
                                          help="Cost price of the product template used for standard stock valuation in accounting and used as a base price on purchase orders.",
                                          groups="base.group_user", string="Cost Price",track_visibility='onchange'),
        'property_account_income': fields.property(
            type='many2one',
            relation='account.account',
            string="Income Account",track_visibility='onchange',
            help="This account will be used for invoices instead of the default one to value sales for the current product."),
        'property_account_expense': fields.property(
            type='many2one',
            relation='account.account',
            string="Expense Account",track_visibility='onchange',
            help="This account will be used for invoices instead of the default one to value expenses for the current product."),
    }


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
        return super(product_template, self).unlink(cr, uid, ids, context=context)

