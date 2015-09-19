# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.tools.translate import _

class config_report_rico(osv.osv):
    
    _name = 'config.report.rico'
    _columns ={
        'account_ids': fields.many2many('account.account', 'account_for_all_market_rel','config_id', 'account_id', 'Account For All Market', required=True),
        'account_id': fields.many2one('account.account', 'Account For Special Market', required=True),
        'categ_id': fields.many2one('res.partner.category', 'Special Market'),
        'categ_ids': fields.many2many('res.partner.category', 'local_categ_rel','config_id', 'categ_id', 'Local Market', required=True),
        'local_account_ids': fields.many2many('account.account', 'account_for_local_market_rel','config_id', 'account_id', 'Account For Local Market', required=True),
    }





