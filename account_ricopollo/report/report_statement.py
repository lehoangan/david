# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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
from openerp.osv import osv
from openerp.report import report_sxw
import time

class report_statement_paser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(report_statement_paser, self).__init__(cr, uid, name, context=context)
        self.number = 0
        self.acumulated = 0
        self.localcontext.update({
            'time': time,
            'get_total': self._get_total,
            'get_data': self._get_data,
            'get_no':self.get_no,
            'get_total_line': self.get_total_line,
        })

    def get_no(self):
       self.number += 1
       return self.number

    def get_total_line(self, amount):
        self.acumulated += amount
        return self.acumulated

    def _get_data(self, statement):
        lines = []
        for line in statement.line_ids:
            lines.append(line)

        return lines

    def _get_total(self, statement_line_ids):
        total = 0.0
        for line in statement_line_ids:
            total += line.amount
        return total


class report_statement2(osv.AbstractModel):
    _name = 'report.account_ricopollo.report_statement'
    _inherit = 'report.abstract_report'
    _template = 'account_ricopollo.report_statement'
    _wrapped_report_class = report_statement_paser



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
