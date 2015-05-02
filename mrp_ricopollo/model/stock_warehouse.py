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
import time

class stock_warehouse(osv.osv):
    _inherit = 'stock.warehouse'

    _columns ={
        'code': fields.char('Farmer Code', 64),
        'manager_id': fields.many2one('res.users', 'Manager'),
        'capacity': fields.integer('Maximum Capacity'),
    }

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
                    ids = [ids]
        reads = self.read(cr, uid, ids, ['name', 'code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = record['code'] + ' ' + name
            res.append((record['id'], name))
        return res

    def onchange_manager(self, cr, uid, ids, manager_id, context):
        if not manager_id:
            return {'value': {}}

        user_obj = self.pool.get('res.users').browse(cr, uid, manager_id, context)

        partner_id = user_obj.partner_id and user_obj.partner_id.id or False

        if partner_id:
            return {'value': {'partner_id': partner_id}}
        else:
            return {'value': {}}