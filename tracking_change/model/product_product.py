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

