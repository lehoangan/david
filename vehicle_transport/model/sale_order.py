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
from openerp.addons.account_bank_statement_extensions.wizard.confirm_statement_line import confirm_statement_line

from openerp.osv import fields, osv
from openerp.tools.translate import _

class sale_order(osv.osv):
    _inherit = "sale.order"

    _columns = {
        "vehicle_id": fields.many2one('fleet.vehicle', 'Vehicle', states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False),
    }

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    _columns = {
                'discount': fields.float('Discount (%)', digits=(16, 12)),
        }
    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):

        res = super(sale_order_line, self)._prepare_order_line_invoice_line(cr, uid, line, account_id, context)
        res.update({'discount_amount': line.discount_amount,})
        return res