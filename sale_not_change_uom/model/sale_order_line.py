# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

class sale_order_line(osv.osv):

    _inherit = "sale.order.line"

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            product_uom_qty = line.product_uom_qty - line.discount_kg
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, product_uom_qty, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    _columns = {
        'discount_kg': fields.float('Discount(KG)', digits_compute= dp.get_precision('Product Price'), readonly=True, states={'draft': [('readonly', False)]}),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
    }

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):

        res = super(sale_order_line, self)._prepare_order_line_invoice_line(cr, uid, line, account_id, context)
        uosqty = self._get_line_qty(cr, uid, line, context=context)
        uos_id = self._get_line_uom(cr, uid, line, context=context)
        res.update({'product_uos_qty': uosqty,
                    'uom_id': uos_id,
                    'quantity': line.product_uom_qty,
                    'uos_id': line.product_uom.id,
                    'price_unit': line.price_unit,
                    'discount_kg': line.discount_kg})
        return res

    #=======================================================================
    # EXTEND: product_id_change
    #==================================================================
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        
        if not product:
            return result
        partner_obj = self.pool.get('res.partner')
        partner = partner_obj.browse(cr, uid, partner_id)
        product_obj = self.pool.get('product.product')
        lang = partner.lang
        context_partner = {'lang': lang, 'partner_id': partner_id}
        product_obj = product_obj.browse(cr, uid, product, context=context_partner)
        if uom and product_obj.uos_id and qty_uos > 1:
            result['value']['product_uos_qty'] = qty_uos
        if not uom and product_obj.uos_id and qty_uos > 0 and qty > 1:
            result['value']['product_uom_qty'] = qty
        return result

    
sale_order_line()
