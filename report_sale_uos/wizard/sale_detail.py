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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
from datetime import datetime
from pytz import timezone
import pytz
from openerp.osv.fields import datetime as datetime_field

class sale_detail_report(osv.osv_memory):
    _name = "sale.detail.report"

    _columns = {
        'partner_id' : fields.many2one('res.partner', 'Cliente'),
        'user_id': fields.many2one('res.users', 'Distribuidor'),
        'date_from': fields.date('Desde'),
        'date_to': fields.date('Hasta'),
        'state': fields.selection([
            ('draft', 'Presupuesto'),
            ('done', 'Orden de Venta'),
            ], 'Tipo de Reporte'),
    }
    _defaults={
    'state': 'draft',
    }

    def _convert_timezone(self, cr, uid, date, context):
        date = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)

        new_date = datetime_field.context_timestamp(cr, uid,
                                                    timestamp=date,
                                                    context=context)
        new_date = datetime.strptime(new_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT), DEFAULT_SERVER_DATETIME_FORMAT)

        duration = new_date - date
        seconds = duration.total_seconds()
        hours = seconds // 3600

        date = date + relativedelta(hours=-hours)
        return date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    # def _get_tz(self, cr, uid, date, context=None):
    #     print context
    #     if context and context.get('tz'):
    #         tz_name = context['tz']
    #     else:
    #         tz_name = self.pool.get('res.users').read(cr, 1, uid, ['tz'])['tz']
    #     att_tz = timezone(tz_name)
    #
    #     attendance_dt = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)
    #     att_tz_dt = pytz.utc.localize(attendance_dt)
    #     att_tz_dt = att_tz_dt.astimezone(att_tz)
    #     att_tz_date_str = datetime.strftime(att_tz_dt, DEFAULT_SERVER_DATETIME_FORMAT)
    #     return att_tz_date_str
    #
    # def remove_7_hours(self, cr, uid, date, context=None):
    #     date = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)
    #     date = date + relativedelta(hours=-7)
    #     date = date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    #     return date

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['form'] = self.read(cr, uid, ids, ['date_from', 'date_to', 'partner_id','state','user_id'])[0]
        data['form'].update({'datetime_from': False, 'datetime_to': False})
        if data['form']['date_from']:
            datetime_from = self._convert_timezone(cr, uid, data['form']['date_from'] + ' 00:00:00', context)
            data['form'].update({'datetime_from': datetime_from})
        if data['form']['date_to']:
            datetime_to = self._convert_timezone(cr, uid, data['form']['date_to'] + ' 23:59:59', context)
            data['form'].update({'datetime_to': datetime_to})

        return self.pool['report'].get_action(cr, uid, [], 'sale_detail_report', data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
