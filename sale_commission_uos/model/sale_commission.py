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

class sale_commission(osv.osv):
    
    _name = 'sale.commission'
    _columns ={
        'name': fields.char('Description', 100),
        'type': fields.selection([('unit', 'Unit'),
                                  ('kg', 'KG')], 'Commission By', required=True),
        'user_ids': fields.many2many('res.users', 'discount_qty_user_rel','disc_id', 'user_id', 'Saleman'),
        'detail_ids': fields.one2many('sale.commission.detail', 'commission_id', 'Details'),

        'account_debit': fields.many2one('account.account', 'Debit Account', required=True, domain=[('type', '!=', 'view')]),
        'account_crebit': fields.many2one('account.account', 'Creadit Account', required=True, domain=[('type', '!=', 'view')]),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True),
    }
    
class sale_commission_detail(osv.osv):
    
    _name = 'sale.commission.detail'
    _columns ={
        'product_ids': fields.many2many('product.product', 'commission_detail_product_rel','commission_id', 'product_id', 'Product', required=True),
        'value': fields.float('Value'),
        'uom_id': fields.many2one('product.uom', 'Per UoM', required=True),
        'commission_id': fields.many2one('sale.commission', 'Sale Commission', required=True),
    }




