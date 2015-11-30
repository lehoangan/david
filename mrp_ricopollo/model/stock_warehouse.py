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
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time

class stock_warehouse(osv.osv):
    _inherit = 'stock.warehouse'

    _columns ={
        'code': fields.char('Farm Code', 64, readonly=True, states={'draft': [('readonly', False)]}),
        'manager_id': fields.many2one('res.users', 'Manager', readonly=True, states={'draft': [('readonly', False)]}),
        'capacity': fields.integer('Maximum Capacity', readonly=True, states={'draft': [('readonly', False)]}),
        'is_farm': fields.boolean('Is Farm', readonly=True, states={'draft': [('readonly', False)]}),
        'account_id': fields.many2one('account.account', 'Farm Account', domain=[('type', '!=', 'view')], readonly=True, states={'draft': [('readonly', False)]}),
        'cycle_ids': fields.one2many('history.cycle.form', 'warehouse_id', 'History Cycle'),
        'state': fields.selection([('draft', 'Close'), ('open', 'Open')], 'State'),
        'journal_id': fields.many2one('account.journal', 'Journal', domain=[('type', '=', 'general')]),
    }
    _order="code desc"

    _defaults={
        'state': 'draft',
    }

    def action_open_cycle(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            if not obj.account_id:
                raise Warning(_('Please set account before'))
            name = self.pool.get('ir.sequence').get(cr, uid, 'history.cycle.form', context=None)
            self.pool.get('history.cycle.form').create(cr, uid, {'name': '%s-%s'%(name, time.strftime('%d%m%y')),
                                                                 'warehouse_id': obj.id,
                                                                 'date_start': time.strftime('%Y-%m-%d')})
        return self.write(cr, uid, ids, {'state': 'open'}, context)

    def action_close_cycle(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            if not obj.account_id:
                raise Warning(_('Please set account before'))
            if obj.account_id.balance != 0:
                raise Warning(_('Account balance = %s. You must transfer it.'%obj.account_id.balance))
            if obj.cycle_ids and not obj.cycle_ids[len(obj.cycle_ids)-1].date_end:
                obj.cycle_ids[len(obj.cycle_ids)-1].write({'date_end': time.strftime('%Y-%m-%d')})
            cr.execute('UPDATE account_move_line set closed_cycle=TRUE where (closed_cycle is null or closed_cycle = FALSE) AND account_id = %s'%obj.account_id.id)
        return self.write(cr, uid, ids, {'state': 'draft'}, context)

    def create(self, cr, uid, vals, context=None):
        new_id = super(stock_warehouse, self).create(cr, uid, vals=vals, context=context)
        if vals.get('account_id', False):
            self.browse(cr, uid, new_id, context).lot_stock_id.write({'account_id': vals['account_id']})
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        new_id = super(stock_warehouse, self).write(cr, uid, ids, vals=vals, context=context)
        if vals.get('account_id', False):
            for id in ids:
                self.browse(cr, uid, id, context).lot_stock_id.write({'account_id': vals['account_id']})
        return new_id


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
                name = '[%s] %s'%(record['code'], name)
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
