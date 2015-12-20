# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time

class unbalance_entry_close_cycle(osv.osv_memory):

    _name = "unbalance.entry.close.cycle"
    _columns ={
        'amount': fields.float('Balance Amount', digits_compute=dp.get_precision('Account')),

        'farmer_account_id': fields.many2one('account.account', 'Farmer Account', required=True, domain=[('type', '!=', 'view')]),
        'other_account_id': fields.many2one('account.account', 'Other Account', required=True, domain=[('type', '!=', 'view')]),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True),
        'name': fields.char('Reference', 100),
    }

    def _default_farmer_account_id(self, cr, uid, context=None):
        if context is None:
            return False
        if not context.get('active_id', False):
            return False
        warehouse = self.pool.get('stock.warehouse').browse(cr, uid, context['active_id'])
        return warehouse.account_id and warehouse.account_id.id or False

    def _default_other_account_id(self, cr, uid, context=None):
        if context is None:
            return False
        account_ids = self.pool.get('account.account').search(cr, uid, [('code', '=', '620000')])
        return account_ids and account_ids[0] or False

    def _default_journal_id(self, cr, uid, context=None):
        if context is None:
            return False
        if not context.get('active_id', False):
            return False
        warehouse = self.pool.get('stock.warehouse').browse(cr, uid, context['active_id'])
        return warehouse.journal_id and warehouse.journal_id.id or False

    def _default_amount(self, cr, uid, context=None):
        if context is None:
            return False
        if not context.get('active_id', False):
            return False
        warehouse = self.pool.get('stock.warehouse').browse(cr, uid, context['active_id'])
        return warehouse.account_id and warehouse.account_id.balance or False

    _defaults={
        'farmer_account_id': _default_farmer_account_id,
        'other_account_id': _default_other_account_id,
        'journal_id': _default_journal_id,
        'amount': _default_amount,
    }

    def _prepare_account_move_line(self, cr, uid, journal_id, period_id,
                                               account_debit, account_credit, amount, date, ref, context):

        name = ref
        result =[]
        if account_credit and account_debit:
            # move line credit
            debit1 = 0
            credit1 = amount
            move_line1 = {
                'name'                  : name,
                'debit'                 : debit1,
                'credit'                : credit1,
                'account_id'            : account_credit,
                'journal_id'            : journal_id,
                'period_id'             : period_id,
                'date'                  : date,
            }
            result.append((0, 0, move_line1))

            #account move line debit
            debit2 = amount
            credit2 = 0
            move_line2 = {
                'name'                  : name,
                'debit'                 : debit2,
                'credit'                : credit2,
                'account_id'            : account_debit,
                'journal_id'            : journal_id,
                'period_id'             : period_id,
                'date'                  : date,
            }
            result.append((0, 0, move_line2))
        return result

    def create_account_move(self, cr, uid, journal_id, name, period_id, date, lst_accout_move_line, context):

        move_pool = self.pool.get('account.move')
        move = {
                'ref': name,
                'journal_id': journal_id,
                'date': date or time.strftime('%Y-%m-%d'),
                'period_id': period_id,
                'line_id': lst_accout_move_line,
                'narration': context.get('note_picking', name),
            }
        move_id = move_pool.create(cr, uid, move, context=context)
        return move_id

    def make_entry(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        warehouse_id = context.get('active_id', False)
        if warehouse_id:
            obj = self.browse(cr, uid, ids, context)
            date = time.strftime('%Y-%m-%d')
            period_ids = self.pool.get('account.period').find(cr, uid, date)
            if not period_ids:
                raise osv.except_osv('Invalid Action', 'You havent defined period for date: %s'%date)
            account_debit = obj.farmer_account_id.id
            account_credit = obj.other_account_id.id
            if obj.amount > 0:
                account_debit = obj.other_account_id.id
                account_credit = obj.farmer_account_id.id

            moves = self._prepare_account_move_line(cr, uid, obj.journal_id.id, period_ids[0],
                                                    account_debit, account_credit, abs(obj.amount), date, obj.name, context)

            move_id = self.create_account_move(cr, uid, obj.journal_id.id, obj.name, period_ids[0], date, moves, context)
            self.pool.get('account.move').button_validate(cr, uid, [move_id], context)

            #update cycle
            obj = self.pool.get('stock.warehouse').browse(cr, uid, warehouse_id, context)
            for cycle in obj.cycle_ids:
                if not cycle.date_end:
                    cycle.write({'date_end': date})
            obj.write({'state': 'draft'})
            cr.execute('UPDATE account_move_line set closed_cycle=TRUE where (closed_cycle is null or closed_cycle = FALSE) AND account_id = %s'%obj.account_id.id)
        return {'type': 'ir.actions.act_window_close'}
