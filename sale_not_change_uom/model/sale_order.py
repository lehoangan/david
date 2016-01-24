# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
import openerp.addons.decimal_precision as dp

class sale_order(osv.osv):

    def _get_default_warehouse(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        warehouse_ids = self.pool.get('stock.warehouse').search(cr, uid, [('company_id', '=', company_id),
                                                                          ('code', '=', 'MAT2-FRIG')], context=context)
        if not warehouse_ids:
            return False
        return warehouse_ids[0]

    def _convert_timezone(self, cr, uid, date, context):
        from datetime import datetime
        from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
        from openerp.osv.fields import datetime as datetime_field
        from dateutil.relativedelta import relativedelta

        date = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)
        new_date = datetime_field.context_timestamp(cr, uid,
                                                    timestamp=date,
                                                    context=context)
        new_date = datetime.strptime(new_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT), DEFAULT_SERVER_DATETIME_FORMAT)

        duration = new_date - date
        seconds = duration.total_seconds()
        hours = seconds // 3600

        date = date + relativedelta(hours=-hours)
        return date.date().strftime(DEFAULT_SERVER_DATE_FORMAT)

    def _get_date(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for so in self.browse(cr, uid, ids, context=context):
            date = self._convert_timezone(cr, uid, so.date_order, context)
            res[so.id] = date
        return res

    _inherit = "sale.order"
    _columns = {
        'is_ok': fields.boolean('Producto Despachado'),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse', required=True),
        'date': fields.function(_get_date, type='date', string='Date', store=True),
                # store={'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['date_order'], 20)},),
    }

    _defaults={
        'is_ok': False,
        'warehouse_id': _get_default_warehouse,
    }

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        res = super(sale_order, self).onchange_partner_id(cr, uid, ids, part, context)
        if part:
            partner = self.pool.get('res.partner').browse(cr, uid, part)
            if partner.r_type == 'X':
                warning = {
                       'title': '',
                       'message' : 'Cliente Bloqueado, Consultar en Oficina Central su estado de cuentas!'
                    }
                res.update({'warning': warning})
        return res

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        invoice_vals = super(sale_order, self)._prepare_invoice(cr, uid, order, lines, context)
        if order.partner_invoice_id.sale_journal_id:
            invoice_vals.update({'journal_id': order.partner_invoice_id.sale_journal_id.id})
        return invoice_vals
