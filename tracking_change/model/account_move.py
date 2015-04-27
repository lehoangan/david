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
import time

class account_move(osv.Model):
    _name = 'account.move'
    _inherit = ['account.move','mail.thread']
    _columns = {
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, states={'posted':[('readonly',True)]},track_visibility='onchange'),
        'date': fields.date('Date', required=True, states={'posted':[('readonly',True)]}, select=True,track_visibility='onchange'),
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'line_id' in vals:
            for order_id in ids:
                self._create_log_message(cr, uid, order_id, vals['line_id'], context)
        res = super(account_move, self).write(cr, uid, ids, vals, context=context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        model_pool = self.pool.get('ir.model')
        model_ids = model_pool.search(cr, uid, [('model', '=', self._name)])
        if model_ids:
            for id in ids:
                self.pool.get('history.delete').create(cr, uid, {'name': self.browse(cr, uid, id).name,
                                                                  'object_id': model_ids[0],
                                                                  'user_id': uid,
                                                                  'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                                                                  'res_id': id})
        return super(account_move, self).unlink(cr, uid, ids, context=context)

    def _create_log_message(self, cr, uid, order_id, data_lines, context=None):
        def format_message(message_description, tracked_values):
            message = ''
            if message_description:
                message = '<span>%s</span>' % message_description
            for name, change in tracked_values.items():
                message += '<div> &nbsp; &nbsp; &bull; <b>%s</b>: ' % change.get('col_info')
                if change.get('old_value'):
                    message += '%s &rarr; ' % change.get('old_value')
                message += '%s</div>' % change.get('new_value')
            return message
        dict_body = {}
        for line in data_lines:
            if not line or not line[2]: continue
            record =  self.pool.get('account.move.line').browse(cr, uid, line[1])
            if 'account_id' in line[2].keys():
                dict_body.update({'account_id': {'new_value': line[2]['account_id'] and self.pool.get('account.account').browse(cr, uid, line[2]['account_id']).name or '', 'col_info': 'Account', 'old_value': record.account_id.name}})
            if 'debit' in line[2].keys():
                dict_body.update({'debit': {'new_value': line[2]['debit'], 'col_info': 'Debit', 'old_value': record.debit}})
            if 'credit' in line[2].keys():
                dict_body.update({'credit': {'new_value': line[2]['credit'], 'col_info': 'Credit', 'old_value': record.credit}})

        if dict_body:
            message = format_message('Other Tracking', dict_body)
            self.message_post(cr, uid, [order_id], body=message, context=context)
        return True

