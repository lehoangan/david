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

{
    'name': 'R - Full Report',
    'version': '1.0',
    'author': 'Anle<lehoangan1988@gmail.com>',
    'category': 'Rico',
    'sequence': 12,
    'description': """
        Not change UoS quantity when change UoM quanity
                    """,
    'images': [],
    'depends': ['sale_not_change_uom','point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_detail_view.xml',
        'wizard/sale_sumary_view.xml',
        'wizard/invoice_detail_view.xml',
        'wizard/payment_detail_view.xml',
        'wizard/discount_client_view.xml',
        'wizard/collector_payment_detail_view.xml',
        'wizard/sale_analysis_view.xml',
        'wizard/accounts_receivable_report.xml',
        'wizard/daily_average_sales_view.xml',
        'wizard/client_status_report_view.xml',
        'wizard/supplier_invoice_total_view.xml',
        'wizard/stock_movement_view.xml',
        
        'view/config_report_rico_view.xml',
        'report/report_define.xml',
        'view/report_so_receipt.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
