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

from openerp.osv import fields, osv

class collector_payment_detail_report(osv.osv_memory):
    _name = "collector.payment.detail.report"

    _columns = {
        'user_id' : fields.many2one('res.users', 'Collector'),
        'date': fields.date('Fecha'),
        'state': fields.selection([
            ('draft', 'Pago Borrador'),
            ('done', ' Pago Efectivo'),
            ], 'Tipo'),
    }
    _defaults={
    'state': 'draft',
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['form'] = self.read(cr, uid, ids, ['date', 'user_id','state'])[0]
        return self.pool['report'].get_action(cr, uid, [], 'collector_payment_detail_report', data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
