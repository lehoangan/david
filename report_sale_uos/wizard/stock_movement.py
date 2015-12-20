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
from openerp.osv.fields import datetime as datetime_field

class stock_movement_report(osv.osv_memory):
    _name = "stock.movement.report"

    _columns = {
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse', required=True),
        'cycle_id': fields.many2one('history.cycle.form', 'Cylce No',
                                        domain="[('warehouse_id', '=', warehouse_id)]"),
        'date_from': fields.date('Fecha desde'),
        'date_to': fields.date('Fecha hasta'),
        'state': fields.selection([('draft', 'Nuevo'),
                                   ('done', 'Realizado'),
                                   ('waiting', 'Esperando otro movimiento'),
                                   ('cancel', 'Cancelado'),
                                   ('assigned', 'Listo para Hacer'),
                                   ('confirmed', 'Esperando disponibilidad')], string='Status'),
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

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['form'] = self.read(cr, uid, ids, [])[0]
        data['form'].update({'datetime_from': False, 'datetime_to': False})
        if data['form']['date_from']:
            datetime_from = self._convert_timezone(cr, uid, data['form']['date_from'] + ' 00:00:00', context)
            data['form'].update({'datetime_from': datetime_from})
        if data['form']['date_to']:
            datetime_to = self._convert_timezone(cr, uid, data['form']['date_to'] + ' 23:59:59', context)
            data['form'].update({'datetime_to': datetime_to})

        if data['form']['cycle_id']:
            cycle = self.pool.get('history.cycle.form').browse(cr, uid, data['form']['cycle_id'][0])
            if cycle.date_start:
                date_start = self._convert_timezone(cr, uid, cycle.date_start + ' 00:00:00', context)
                if (data['form']['datetime_from'] and date_start > data['form']['datetime_from']) or not data['form']['datetime_from']:
                        data['form']['datetime_from'] = date_start
            if cycle.date_end:
                date_end = self._convert_timezone(cr, uid, cycle.date_end + ' 23:59:59', context)
                if (data['form']['datetime_to'] and date_end < data['form']['datetime_to']) or not data['form']['datetime_to']:
                        data['form']['datetime_to'] = date_end
        return self.pool['report'].get_action(cr, uid, [], 'stock_movement_report', data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
