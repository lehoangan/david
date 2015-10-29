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
import openerp.addons.decimal_precision as dp

class account_voucher_line(osv.Model):

    def _remain_balance(self, cr, uid, ids, field_name, arg, context=None):
        res = {}.fromkeys(ids, 0)
        for line in self.browse(cr, uid, ids, context):
             res.update({line.id: line.amount_unreconciled - line.amount})
        return res

    _inherit = 'account.voucher.line'
    _columns = {
        'remain_balance':fields.function(_remain_balance, string="Saldo", type='float'),
    }

    def onchange_amount(self, cr, uid, ids, amount, amount_unreconciled, context=None):
        res = super(account_voucher_line, self).onchange_amount(cr, uid, ids, amount, amount_unreconciled, context)
        res['value'].update({'remain_balance': amount_unreconciled - amount,
                             'amount': amount})
        return res

