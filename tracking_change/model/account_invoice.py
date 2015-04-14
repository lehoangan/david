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

class account_invoice(osv.Model):

    _inherit = 'account.invoice'
    
    def write(self, cr, uid, ids, vals, context=None):
        message = '<span>%s</span>' % 'Other Tracking'
        self.message_post(cr, uid, ids, body=message, context=context)
        res = super(account_invoice, self).write(cr, uid, ids, vals, context=context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        model_pool = self.pool.get('ir.model')
        model_ids = model_pool.search(cr, uid, [('model', '=', self._name)])
        if model_ids:
            for id in ids:
                self.pool.get('history.delete').create(cr, uid, {'name': self.browse(cr, uid, id).number or self.browse(cr, uid, id).origin,
                                                                  'object_id': model_ids[0],
                                                                  'user_id': uid,
                                                                  'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                                                                  'res_id': id})
        return super(account_invoice, self).unlink(cr, uid, ids, context=context)

class account_voucher(osv.Model):

    _inherit = 'account.voucher'

    def write(self, cr, uid, ids, vals, context=None):
        message = '<span>%s</span>' % 'Other Tracking'
        self.message_post(cr, uid, ids, body=message, context=context)
        res = super(account_voucher, self).write(cr, uid, ids, vals, context=context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        model_pool = self.pool.get('ir.model')
        model_ids = model_pool.search(cr, uid, [('model', '=', self._name)])
        if model_ids:
            for id in ids:
                self.pool.get('history.delete').create(cr, uid, {'name': self.browse(cr, uid, id).number or self.browse(cr, uid, id).name,
                                                                  'object_id': model_ids[0],
                                                                  'user_id': uid,
                                                                  'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                                                                  'res_id': id})
        return super(account_voucher, self).unlink(cr, uid, ids, context=context)


