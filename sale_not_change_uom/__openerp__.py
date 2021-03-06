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
    'name': 'R - SALE',
    'version': '1.0',
    'author': 'Anle<lehoangan1988@gmail.com>',
    'category': 'Rico',
    'sequence': 12,
    'description': """
        Not change UoS quantity when change UoM quanity
                    """,
    'images': [],
    'depends': ['sale_stock', 'sale_layout', 'account'],
    'data': [
        'view/sale_stock_view.xml',
        'view/report_saleorder.xml',
        'view/sale_order_view.xml',
        'view/account_invoice_view.xml',
        'view/report_invoice.xml',
        'view/res_partner_view.xml',
        'report/sale_report_view.xml',
        'rico_security.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
