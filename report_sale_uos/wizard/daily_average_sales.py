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

from openerp.osv import fields, osv
import datetime
from openerp.tools.translate import _

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class daily_average_sales(osv.osv_memory):
    _name = "daily.average.sales"

    _columns = {
        'partner_id' : fields.many2one('res.partner', 'Cliente'),
        'date_from': fields.date('Desde', required=True),
        'date_to': fields.date('Hasta', required=True),
        'inv_state': fields.selection([
            ('draft', 'Factura Borrador'),
            ('open', 'Abierto'),
            ('paid', 'Pagado'),
            ('all', ' Abierto + Pagado'),
            ], 'Tipo de Boleta'),
    }
    _defaults={
    'inv_state': 'all',
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['form'] = self.read(cr, uid, ids, ['date_from', 'date_to', 'partner_id','inv_state'])[0]
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        date_from = datetime.datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT)
        date_to = datetime.datetime.strptime(date_to, DEFAULT_SERVER_DATE_FORMAT)

        if date_from.strftime("%a") != 'Mon':
            raise osv.except_osv(_('User Error!'), _('%s start must be monday.(%s)'%(date_from, date_from.strftime("%a"))))
        if date_to.strftime("%a") != 'Sun':
            raise osv.except_osv(_('User Error!'), _('%s start must be sunday.(%s)'%(date_to, date_to.strftime("%a"))))
        lst_date = []
        while date_from < date_to:
            lst_date.append([date_from.strftime(DEFAULT_SERVER_DATE_FORMAT),(date_from +datetime.timedelta(days=6)).strftime(DEFAULT_SERVER_DATE_FORMAT)])
            date_from = date_from +datetime.timedelta(days=7)
        data['form'].update({'lst_date': lst_date})

        return self.pool['report'].get_action(cr, uid, [], 'daily_average_sales_report', data=data, context=context)
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
