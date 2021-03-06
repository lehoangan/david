# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
{
    'name': 'R - Bank Deposit',
    'category': 'Generic Modules/Accounting',
    'author': 'Anle<lehoangan1988@gmail.com>',
    'depends': ['account_cancel'],
    'init_xml': [],
    'update_xml': [
        'security/ir.model.access.csv',
        'view/account_make_deposit_view.xml',
        'report/report_define.xml',
        'wizard/collected_control_view.xml',
				   ],
    'test': [],
    'active': False,
    'installable': True,
    'certificate':''
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
