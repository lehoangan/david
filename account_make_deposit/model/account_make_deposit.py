# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
import time

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class bank_deposit(osv.osv):
    _name = "bank.deposit"


    def unlink(self, cr, uid, ids, context=None):
        self.remove_all(cr, uid, ids, context=context) # Call the method necessary to remove the changes made earlier
        return super(bank_deposit, self).unlink(cr, uid, ids, context=context)

    def action_cancel(self, cr, uid, ids, context=None):
        self.remove_all(cr, uid, ids, context=context) # Call the method necessary to remove the changes made earlier
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True

    def action_process(self, cr, uid, ids, context=None):
        move_lines = []
        for deposit in self.browse(cr, uid, ids, context=context):
            if not deposit.journal_id.sequence_id:
                raise osv.except_osv(_('Error !'), _('Please define sequence on deposit journal'))
            if deposit.journal_id.centralisation:
                raise osv.except_osv(_('UserError'),
                        _('Cannot create move on centralised journal'))

            # Create the move lines first
            move_lines.append((0,0, self.get_move_line(cr, uid, deposit, 'src')))
            move_lines.append((0, 0, self.get_move_line(cr, uid, deposit, 'dest')))
            # Create the move for the deposit
            move = {
                'ref': deposit.deposit_no,
                'name': '/',
                'line_id': move_lines,
                'journal_id': deposit.journal_id.id,
                'date': deposit.date,
                'narration': deposit.ref,
            }
            move_id = self.pool.get('account.move').create(cr, uid, move, context=context)
            # Post the account move
            self.pool.get('account.move').post(cr, uid, [move_id])
            # Link the move with the deposit and populate other fields
            self.write(cr, uid, [deposit.id], {'move_id': move_id,
                                              'state': 'done'},
                                              context=context)
        return True

    def get_move_line(self, cr, uid, deposit, type, context=None):
        return {
            'type': type,
            'name': deposit.name or '/',
            'debit': type == 'dest' and deposit.amount or 0.0,
            'credit': type == 'src' and deposit.amount or 0.0,
            'account_id': type == 'src' and deposit.deposit_from_account_id.id or deposit.deposit_to_account_id.id,
            'date': deposit.date,
            'ref': deposit.deposit_no or '',
        }

    def remove_all(self, cr, uid, ids, context=None):
        account_move_obj = self.pool.get('account.move')
        for deposit in self.browse(cr, uid, ids, context=context):
            if deposit.move_id:
                account_move_obj.button_cancel(cr, uid, [deposit.move_id.id], context=context) # Cancel the posted account move
                account_move_obj.unlink(cr, uid, [deposit.move_id.id], context=context) # Finally, delete the account move
        return True

    def action_cancel_draft(self, cr, uid, ids, context=None):
        self.remove_all(cr, uid, ids, context=context) # Call the method necessary to remove the changes made earlier
        self.write(cr, uid, ids, {'state': 'draft'},
                                  context=context)
        return True

    def _get_period(self, cr, uid, context=None):
        periods = self.pool.get('account.period').find(cr, uid)
        return periods and periods[0] or False

    def _get_amount(self, cr, uid, ids, name, args, context=None):
        res = {}
        for deposit in self.browse(cr, uid, ids, context=context):
            sum = 0.0
            for line in deposit.ticket_line_ids:
                sum += line.amount
            res[deposit.id] = sum
        return res

    def _get_count_total(self, cr, uid, ids, name, args, context=None):
        res = {}
        for deposit in self.browse(cr, uid, ids, context=context):
            res[deposit.id] = len(deposit.ticket_line_ids)
        return res

    _columns = {

        'name': fields.char('Memo', size=64, states={'done':[('readonly', True)]}, help="Memo for the deposit ticket"),
        'deposit_to_account_id': fields.many2one('account.account', 'Bank Account', required=True,
                                                 states={'done':[('readonly', True)]}, domain="[('company_id', '=', company_id), ('type', '!=', 'view')]",
                                                 help="The Bank/Gl Account the Deposit is being made to."),
        'deposit_from_account_id': fields.many2one('account.account', 'Collector Account', required=True,
                                                   states={'done':[('readonly', True)]}, domain="[('company_id', '=', company_id), ('type', '!=', 'view')]",
                                                   help="The Bank/GL Account the Payments are currently found in."),
        'date': fields.date('Date of Deposit', required=True, states={'done':[('readonly', True)]}, help="The Date of the Deposit Ticket."),

        'journal_id': fields.many2one('account.journal', 'Journal', required=True, states={'done':[('readonly', True)]},
                                      help="The Journal to hold accounting entries."),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True,
                                      help="The Company for which the deposit ticket is made to"),
        'period_id': fields.many2one('account.period', 'Force Period', required=True,
                                     states={'done':[('readonly', True)]},
                                     help="Keep empty to use the period of the validation date.",),
        'user_id': fields.many2one('res.users', 'Prepared By', states={'done':[('readonly', True)]}),

        'deposit_no': fields.char('Number', size=64, states={'done':[('readonly', True)]}),
        'ref': fields.char('Ref #', size=64),
        'move_id': fields.many2one('account.move', 'Journal Entry', readonly=True, select=1, help="Link to the automatically generated Journal Items."),

        'ticket_line_ids': fields.one2many('bank.deposit.line', 'deposit_id', 'Deposit Ticket Line', states={'done':[('readonly', True)]}),
        'amount': fields.function(_get_amount, method=True, string='Amount', digits_compute=dp.get_precision('Account'),
                                  type='float', help="Calculates the Total of All Deposit Lines – This is the Total Amount of Deposit."),
        'state': fields.selection([
            ('draft','Draft'),
            ('done','Done'),
            ('cancel', 'Cancel')
            ],'State', select=True, readonly=True),
    }
    _defaults = {
        'state': 'draft',
        'period_id': _get_period,
        'date': time.strftime('%Y-%m-%d'),
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        'user_id': lambda self, cr, uid, c: uid,
    }
    _order = "date desc" # the most recent deposits displays first

bank_deposit()

class bank_deposit_line(osv.osv):
    _name = "bank.deposit.line"
    _columns = {
        'partner_id': fields.many2one('res.partner', string='Partner', help="Derived from related Journal Item."),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Account'),
                               help="Derived from the 'debit' amount from related Journal Item."),
        'deposit_id': fields.many2one('bank.deposit', 'Deposit Ticket', required=True, ondelete='cascade'),
        'company_id': fields.related('deposit_id', 'company_id', type='many2one', relation='res.company', string='Company', readonly=True,
                                     help="Derived from related Journal Item."),
    }

bank_deposit_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
