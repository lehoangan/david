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

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class account_invoice(models.Model):
    _inherit = "account.invoice"

    commission_entry_id = fields.Many2one('account.move', string='Commission Entry',copy=False, readonly=True)


    # @api.v7
    # def invoice_validate(self, cr, uid, ids, context=None):
    #     recs = self.browse(cr, uid, ids, context)
    #     return recs.pay_and_reconcile(pay_amount, pay_account_id, period_id, pay_journal_id,
    #                 writeoff_acc_id, writeoff_period_id, writeoff_journal_id, name=name)
    @api.multi
    def action_cancel(self):
        res = super(account_invoice, self).action_cancel()
        moves = self.env['account.move']
        for inv in self:
            if inv.commission_entry_id:
                moves += inv.commission_entry_id
        if moves:
            moves.button_cancel()
            moves.unlink()
        return res

    @api.multi
    def invoice_validate(self):
        if self.type != 'out_invoice':
            return super(account_invoice, self).invoice_validate()

        commission_obj = self.env['sale.commission']
        commission_detail_obj = self.env['sale.commission.detail']
        commission_ids = commission_obj.search([('user_ids', '=', self.user_id.id)])
        if not commission_ids:
            commission_ids = commission_obj.search([('user_ids', '=', False)])
        amount = 0
        account_debit, account_crebit = False, False
        journal_id = False
        for commission in commission_ids:
            account_debit, account_crebit = commission.account_debit.id, commission.account_crebit.id
            journal_id=  commission.journal_id.id
            for invl in self.invoice_line:
                if invl.product_id:
                    if commission.type == 'unit' and invl.uom_id:
                        condition = [('commission_id', '=', commission.id),
                                    ('product_ids', '=', invl.product_id.id),
                                    ('uom_id', '=', invl.uom_id.id)]
                        detail_ids = commission_detail_obj.search(condition)
                        for detail in detail_ids:
                            amount += invl.product_uos_qty * detail.value
                    elif commission.type == 'kg' and invl.uos_id:
                        condition = [('commission_id', '=', commission.id),
                                    ('product_ids', '=', invl.product_id.id),
                                    ('uom_id', '=', invl.uos_id.id)]
                        detail_ids = commission_detail_obj.search(condition)
                        for detail in detail_ids:
                             amount += invl.quantity * detail.value
        if amount and account_debit and account_crebit:
            period_ids = self.env['account.period'].search([('date_start', '<=', self.date_invoice), ('date_stop', '>=', self.date_invoice)])
            if period_ids:
                lst_accout_move_line = self._prepare_account_move_line(journal_id, amount, period_ids[0].id, \
                                              account_debit, account_crebit, self.date_invoice, self.user_id.partner_id.id)
                move_id = self.create_account_move(journal_id, period_ids[0].id, self.date_invoice, lst_accout_move_line)
                self.write({'commission_entry_id': move_id.id})
                moves = self.env['account.move'].browse(move_id.id)
                moves.button_validate()
        return super(account_invoice, self).invoice_validate()

    def create_account_move(self, journal_id, period_id, date, lst_accout_move_line):

        move_pool = self.env['account.move']
        description = 'Commission Entry For INV: %s'%self.number
        move = {
                'ref': description,
                'name': description,
                'journal_id': journal_id,
                'date': date,
                'period_id': period_id,
                'line_id': lst_accout_move_line,
                'narration': 'description',
            }
        move_id = move_pool.create(move)
        return move_id

    def _prepare_account_move_line(self,journal_id, amount, period_id, \
                                       account_debit, account_crebit, date, partner_id):

        result = []
        if account_crebit and account_debit:
            # move line credit
            name = 'Commission Entry'
            move_line1 = {
                'name'                  : name,
                'debit'                 : 0,
                'credit'                : amount,
                'account_id'            : account_crebit,
                'journal_id'            : journal_id,
                'period_id'             : period_id,
                'date'                  : date,
                'partner_id'            : partner_id,
            }
            result.append((0, 0, move_line1))
            #account move line debit
            move_line2 = {
                'name'  : name,
                'debit'                 : amount,
                'credit'                : 0,
                'account_id'            : account_debit,
                'journal_id'            : journal_id,
                'period_id'             : period_id,
                'date'                  : date,
                'partner_id'            : partner_id,
            }
            result.append((0, 0, move_line2))

        return result
