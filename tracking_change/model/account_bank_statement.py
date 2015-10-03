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
import openerp.addons.decimal_precision as dp

class account_bank_statement(osv.Model):

    _inherit = 'account.bank.statement'

    _columns = {
        'balance_start': fields.float('Starting Balance', digits_compute=dp.get_precision('Account'),
            states={'confirm':[('readonly',True)]},track_visibility='onchange'),
        'balance_end_real': fields.float('Ending Balance', digits_compute=dp.get_precision('Account'),
            states={'confirm': [('readonly', True)]}, help="Computed using the cash control lines",track_visibility='onchange'),
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'line_ids' in vals:
            for order_id in ids:
                self._create_log_message(cr, uid, order_id, vals['line_ids'], context)
        res = super(account_bank_statement, self).write(cr, uid, ids, vals, context=context)
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
        return super(account_bank_statement, self).unlink(cr, uid, ids, context=context)

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
            record =  self.pool.get('account.bank.statement.line').browse(cr, uid, line[1])
            if 'date' in line[2].keys():
                dict_body.update({'date': {'new_value': line[2]['date'], 'col_info': 'Line Date', 'old_value': record.date}})
            if 'name' in line[2].keys():
                dict_body.update({'name': {'new_value': line[2]['name'], 'col_info': 'Desc', 'old_value': record.name}})
            if 'partner_id' in line[2].keys():
                partner = ''
                if line[2]['partner_id']:
                    partner = self.pool.get('res.partner').browse(cr, uid, line[2]['partner_id']).name
                dict_body.update({'partner_id': {'new_value': partner, 'col_info': 'Partner', 'old_value': record.partner_id and record.partner_id.name or ''}})
            if 'amount' in line[2].keys():
                dict_body.update({'amount': {'new_value': line[2]['amount'], 'col_info': 'Monto', 'old_value': record.amount}})
        message = format_message('Other Tracking', dict_body)
        if message:
            self.message_post(cr, uid, [order_id], body=message, context=context)
        return True

