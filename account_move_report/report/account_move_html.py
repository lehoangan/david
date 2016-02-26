# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# ##############Credits######################################################
#    Coded by: Luis Ernesto García (ernesto_gm@vauxoo.com)
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
from openerp.report import report_sxw
import time
from .webkit_parser_header_fix import HeaderFooterTextWebKitParser


class account_move_report_html(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(account_move_report_html, self).__init__(cr, uid, name,
                                context=context)
        self.localcontext.update({
            'time': time,
            'get_total_debit_credit': self.get_total_debit_credit,
            'get_note': self.get_note,
        })

    def get_total_debit_credit(self, line_ids):
        sum_tot_debit = 0.00
        sum_tot_credit = 0.00
        for line in line_ids:
            sum_tot_debit += (line.debit)
            sum_tot_credit += (line.credit)
        return {'sum_tot_debit': sum_tot_debit, 'sum_tot_credit': sum_tot_credit}

    def get_inv_note(self, move_id):
        cr, uid = self.cr, self.uid
        invoice_obj = self.pool.get('account.invoice')
        invoice_ids = invoice_obj.search(cr, uid, [('move_id', '=', move_id)])
        invoice_note = ''
        if invoice_ids:
            invoice = invoice_obj.browse(cr, uid, invoice_ids[0])
            invoice_note = invoice.comment
        return invoice_note

    def get_note(self, move_id):
        cr, uid = self.cr, self.uid
        invoice_obj = self.pool.get('account.invoice')
        voucher_obj = self.pool.get('account.voucher')
        invoice_ids = invoice_obj.search(cr, uid, [('move_id', '=', move_id)])
        invoice_note = []
        move_note = []
        if invoice_ids:
            invoice = invoice_obj.browse(cr, uid, invoice_ids[0])
            invoice_note.append(invoice.comment)

            for payment in invoice.payment_ids:
                if payment.move_id.narration and payment.move_id.narration not in move_note:
                    move_note.append(payment.move_id.narration)
        else:
            voucher_ids = voucher_obj.search(cr, uid, [('move_id', '=', move_id)])
            if voucher_ids:
                voucher = voucher_obj.browse(cr, uid, voucher_ids[0])
                move_note.append(voucher.narration or '')
                for line in voucher.line_ids:
                    if line.amount:
                        invoice_note.append(self.get_inv_note(line.move_line_id.move_id.id))
        return ' - '.join(invoice_note), ' - '.join(move_note)

HeaderFooterTextWebKitParser(
    'report.account.move.report.webkit',
    'account.move',
    'addons/report_account_move/report/account_move_report_html.mako',
    parser=account_move_report_html)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
