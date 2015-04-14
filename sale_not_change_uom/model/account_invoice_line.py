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


from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp

class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"

    @api.one
    @api.depends('price_unit', 'discount','discount_kg', 'invoice_line_tax_id', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id')
    def _compute_price(self):
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = self.invoice_line_tax_id.compute_all(price, self.quantity-self.discount_kg, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = taxes['total']
        if self.invoice_id:
            self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)

    price_subtotal = fields.Float(string='Amount', digits= dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_price')
    product_uos_qty = fields.Float(string='Quantity (UoS)', digits= dp.get_precision('Product Unit of Measure'),
        required=True, default=1)
    discount_kg = fields.Float(string='Discount(KG)', digits= dp.get_precision('Discount'),
        default=0.0)
    uom_id = fields.Many2one('product.uom', string='UoS',
        ondelete='set null', index=True)


