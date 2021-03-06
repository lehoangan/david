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

class account_bank_statement(osv.Model):

    _inherit = 'account.bank.statement'

    def _all_lines_reconciled(self, cr, uid, ids, name, args, context=None):
        res = {}
        for statement in self.browse(cr, uid, ids, context=context):
            res[statement.id] = all([line.journal_entry_id.id or line.account_id.id for line in statement.line_ids])
        return res

    _columns = {
        'all_lines_reconciled': fields.function(_all_lines_reconciled, string='All lines reconciled', type='boolean'),
    }


class account_bank_statement_line(osv.Model):

    _inherit = 'account.bank.statement.line'

    _columns = {
        'account_id': fields.many2one('account.account', 'Account', domain=[('type', '!=', 'view')])
    }
    

