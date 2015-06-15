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
import openerp
import time

class history_cycle_form(osv.osv):
    _name = 'history.cycle.form'
    _inherit = ['mail.thread']

    _columns = {
        'name': fields.char('Cylce No', 100, required=True),
        'type': fields.selection([('Male', 'Macho'), ('female', 'Hembra'), ('mixed', 'Mixto')], 'Type'),
        'date_start': fields.date('Date Start', required=True),
        'date_end': fields.date('Date End'),
        'warehouse_id':fields.many2one('stock.warehouse', 'Parent', ondelete='cascade'),
    }

    _defaults= {
        'date': time.strftime('%Y-%m-%d'),
    }

    def write(self, cr, uid, ids, vals, context=None):
        for obj in self.browse(cr, uid, ids, context):
            if obj.date_state and vals.get('date_start', False) and \
                    not self.pool['res.users'].has_group(cr, uid, 'base.group_edit_date_history_cycle'):
                raise openerp.exceptions.AccessError(_("You is not allowed for edit date start"))
            elif obj.date_end and vals.get('date_end', False) and \
                    not self.pool['res.users'].has_group(cr, uid, 'base.group_edit_date_history_cycle'):
                raise openerp.exceptions.AccessError(_("You is not allowed for edit date stop"))
        return super(history_cycle_form, self).write(cr, uid, ids, vals, context)
