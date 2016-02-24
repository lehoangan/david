##############################################################################
#
# Copyright (c) 2008-2011 Alistek Ltd (http://www.alistek.com) All Rights Reserved.
#                    General contacts <info@alistek.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This module is GPLv3 or newer and incompatible
# with OpenERP SA "AGPL + Private Use License"!
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.report import report_sxw

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_detail': self.get_detail,
            'get_collector': self.get_collector,
        })

    def get_collector(self, form):
        where_str = ''
        if form['date_end']:
            where_str = " AND inv.date_invoice <= '%s' "%form['date_end']

        if form['journal_id']:
            where_str += " AND journal.id = %s "%form['journal_id'][0]

        select_str = """
                 SELECT ROW_NUMBER() OVER(ORDER BY id) AS no, tmp.* FROM (
                  SELECT DISTINCT(collected_journal_id) as id, journal.name FROM res_partner part
                        JOIN account_invoice inv on (inv.partner_id = part.id)
                        JOIN account_journal journal on (journal.id = part.collected_journal_id)
                        WHERE inv.state = 'open' %s ) tmp
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res

    def get_date(self, form):
        from datetime import datetime,timedelta
        from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

        date_start = datetime.strptime(form['date_start'], DEFAULT_SERVER_DATE_FORMAT)
        res = [date_start]
        date_next = form['date_start']
        while date_next < form['date_end']:
            date_start = date_start + timedelta(days=1)
            date_next = date_start.strftime(DEFAULT_SERVER_DATE_FORMAT)
            res += [date_start]
        return res

    def get_detail(self, form, journal_id):
        res = []
        cr = self.cr
        uid = self.uid
        invoice_obj = self.pool.get('account.invoice')
        deposit_obj = self.pool.get('bank.deposit')
        for date in self.get_date(form):
            invoice_ids = invoice_obj.search(cr, uid, [('state', '=', 'open'),
                                                       ('date_invoice', '<=', date),
                                                       ('partner_id.collected_journal_id', '=', journal_id)])
            unpaid, paid = 0, 0

            for invoice in invoice_obj.browse(cr, uid, invoice_ids):
                unpaid += invoice.residual
                paid += (invoice.amount_total - invoice.residual)

            deposit_ids = deposit_obj.search(cr, uid, [('date', '=', date),
                                                       ('journal_id', '=', journal_id),
                                                       ('state', '=', 'done')])
            total_deposit = 0
            name = []
            ref = []
            bank_ref = []
            for deposit in deposit_obj.browse(cr, uid, deposit_ids):
                total_deposit += deposit.amount
                name += [deposit.move_id.name]
                if deposit.ref:
                    ref += [deposit.ref]
                if deposit.name:
                    bank_ref += [deposit.name]
            data = {'unpaid': unpaid,
                      'paid': paid,
                      'deposit': total_deposit,
                      'balance': paid - total_deposit,
                      'entry': '-'.join(name),
                      'ref': '-'.join(ref),
                      'bank_ref': '-'.join(bank_ref),
                      'balance2': unpaid - paid,
                      'percent': round((unpaid - paid)/unpaid * 100, 2)
                      }
            res.append(data)

        return res

