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

class accounts_receivable_report(osv.osv_memory):
    _name = "accounts.receivable.report"

    _columns = {
        'tag_ids' : fields.many2many('res.partner.category', 'partner_tag_reciveble_report', 'report_id', 'tag_id', 'Mercado'),
        'date_from': fields.date('Desde', required=True),
        'date_to': fields.date('Hasta', required=True),
        'type': fields.selection([
            ('client', 'Solo Clientes'),
            ('product', 'Con Productos'),
            ], 'Mostrar'),
    }
    _defaults={
    'type': 'client',
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['form'] = self.read(cr, uid, ids, ['date_from', 'date_to', 'tag_ids','type'])[0]
        return self.pool['report'].get_action(cr, uid, [], 'accounts_receivable_report', data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
