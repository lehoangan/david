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
{
    'name': 'MRP OF RICOPOLLOs',
    'version': '1.0',
    'author': 'OpenERPVN',
    'category': 'MRP',
    'website': 'https://www.odoo.com',
    'description': """
            1. Make request form for farm to FAB
    """,
    'depends': ["mrp"],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'view/mrp_request_form_view.xml',
        'wizard/merge_to_make_mo_view.xml'],
    'auto_install': False,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
