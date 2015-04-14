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

import time
from openerp.osv import osv
from openerp.report import report_sxw


class order(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(order, self).__init__(cr, uid, name, context=context)

        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        partner = user.company_id.partner_id

        self.localcontext.update({
            'time': time,
            'total_amount': self.total_amount,
            'net': self.netamount,
            'address': partner or False,
        })

    def netamount(self, order_line_id):
        sql = 'select (product_uom_qty*price_unit) as net_price from sale_order_line where id = %s'
        self.cr.execute(sql, (order_line_id,))
        res = self.cr.fetchone()
        print res, '=================='
        return res[0]

    def total_amount(self, order_id):
        print order_id
        sql = 'select sum(product_uom_qty*price_unit) as price from sale_order_line where order_id = %s'
        self.cr.execute(sql, (order_id,))
        res = self.cr.fetchone()
        print res, '=================='
        return res[0]


class report_order_receipt(osv.AbstractModel):
    _name = 'report.report_sale_uos.report_so_receipt'
    _inherit = 'report.abstract_report'
    _template = 'report_sale_uos.report_so_receipt'
    _wrapped_report_class = order

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
