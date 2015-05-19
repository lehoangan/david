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

class invoice_detail_report(osv.osv_memory):
    _name = "invoice.detail.report"

    _columns = {
        'partner_id' : fields.many2one('res.partner', 'Cliente'),
        'date_from': fields.date('Desde'),
        'date_to': fields.date('Hasta'),
        'type': fields.selection([
            ('completo', 'Completo'),
            ('consolidado', ' Consolidado'),
            ], 'Tipo'),
        'state': fields.selection([
            ('draft', 'Factura Borrador'),
            ('done', ' Factura'),
            ], 'Factura Tipo'),
        'inv_state': fields.selection([
            ('open', 'Abierto'),
            ('paid', ' Pagado'),
            ('all', ' Abierto + Pagado'),
            ], 'Tipo de Boleta'),
    }
    _defaults={
    'state': 'draft',
    'type': 'completo',
    'inv_state': 'all',
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['form'] = self.read(cr, uid, ids, ['date_from', 'date_to', 'partner_id','state','inv_state','type'])[0]
        if data['form']['type'] == 'completo':
            return self.pool['report'].get_action(cr, uid, [], 'invoice_detail_report', data=data, context=context)
        else:
            return self.pool['report'].get_action(cr, uid, [], 'invoice_total_report', data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
