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

from openerp.osv import osv
from openerp.tools.translate import _

class account_invoice_confirm(osv.osv_memory):
    """
    This wizard will confirm the all the selected draft invoices
    """

    _inherit = "account.invoice.confirm"

    def invoice_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids', []) or []

        proxy = self.pool['account.invoice']
        non_validated_ids = []
        for record in proxy.browse(cr, uid, active_ids, context=context):
            if record.state not in ('draft', 'proforma', 'proforma2'):
                raise osv.except_osv(_('Warning!'), _("Selected invoice(s) cannot be confirmed as they are not in 'Draft' or 'Pro-Forma' state."))

            old_ids = proxy.search(cr, uid, [('partner_id', '=', record.partner_id.id), ('state', '=', 'open')])
            if record.partner_id.warning_invoice and len(old_ids) >= record.partner_id.warning_invoice:
                non_validated_ids += [record.id]
                continue
            record.signal_workflow('invoice_open')
        if not non_validated_ids:
            return {'type': 'ir.actions.act_window_close'}
        else:
            mod_obj = self.pool.get('ir.model.data')
            act_obj = self.pool.get('ir.actions.act_window')
            result = mod_obj.get_object_reference(cr, uid, 'account', 'action_invoice_tree1')
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
            result['domain'] = "[('id','in', [" + ','.join(map(str, non_validated_ids)) + "])]"
            return result

