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

class daily_consumption_form(osv.osv):
    _name = 'daily.consumption'
    _inherit = ['mail.thread']

    _columns ={        
        'name': fields.char('Ref', 100, readonly=True, states={'draft': [('readonly', False)]}),
        'description': fields.char('Notas', 100, readonly=True, states={'draft': [('readonly', False)]}),
        'warehouse_id': fields.many2one('stock.warehouse', 'Código de Granja', required=True,
                                        domain=[('state', '=', 'open')],
                                        readonly=True, states={'draft': [('readonly', False)]}),
        'cycle_id': fields.many2one('history.cycle.form', 'Cylce No', required=True,
                                        domain="[('warehouse_id', '=', warehouse_id), ('date_end', '=', False)]",
                                        readonly=True, states={'draft': [('readonly', False)]}),
        'date': fields.date('Fecha', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', 'Create By', readonly=True),
        'consumption_line_ids': fields.one2many('daily.consumption.material', 'consumption_id', 'Consumption Material', readonly=True, states={'draft': [('readonly', False)]}),
        'dead_line_ids': fields.one2many('daily.consumption.dead', 'consumption_id', 'Chicken Dead', readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Borrador'),
            ('approve', 'Aprobar'),
            ('cancel', 'Cancelar'),
            ], 'Status', readonly=True,select=True),
    }

    _order="date desc"

    _defaults= {
        'state': 'draft',
        'user_id': lambda self,cr,uid,context=None: uid,
        'date': time.strftime('%Y-%m-%d'),
    }

    def action_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel',})

    def action_set_to_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft',})

    def action_approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'approve'})
    
