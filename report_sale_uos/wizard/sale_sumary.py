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

class sale_sumary_report(osv.osv_memory):
    _name = "sale.sumary.report"

    _columns = {
        'date_from': fields.date('Desde', required=True),
        'date_to': fields.date('Hasta', required=True),
        'product_ids': fields.many2many('product.product', 'report_sale_product',
                                        'sale_id', 'product_id', 'Product',
                                        domain=[('sale_ok', '=', True)]),
        'state': fields.selection([
            ('draft', 'Presupuesto'),
            ('done', ' Orden de Venta'),
            ], 'Tipo'),
        'invoice_state': fields.selection([
            ('draft', 'Factura Borrador'),
            ('done', ' Factura'),
            ('both', 'Ambos')
            ], 'Factura Tipo'),
    }
    _defaults={
        'state': 'done',
    }

    def remove_7_hours(self, cr, uid, date, context=None):
        from openerp.osv.fields import datetime as datetime_field
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
        data['form'] = self.read(cr, uid, ids, ['date_from', 'date_to', 'state', 'product_ids','invoice_state'])[0]
        datetime_from = self.remove_7_hours(cr, uid, data['form']['date_from'] + ' 00:00:00', context)
        datetime_to = self.remove_7_hours(cr, uid, data['form']['date_to'] + ' 23:59:59', context)
        data['form'].update({'datetime_from': datetime_from,
                             'datetime_to': datetime_to})
        return self.pool['report'].get_action(cr, uid, [], 'sale_sumary_report', data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
