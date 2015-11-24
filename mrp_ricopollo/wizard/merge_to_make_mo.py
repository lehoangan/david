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

from openerp.osv import osv, fields
from openerp.tools.translate import _

class merge_to_make_mo(osv.osv_memory):

    _name = "merge.to.make.mo"
    _columns ={
        "location_src_id": fields.many2one('stock.location', 'Raw Materials Location', required=True, domain=[('type', '=', 'internal')]),
        "location_dest_id": fields.many2one('stock.location', 'Finished Products Location', required=True, domain=[('type', '=', 'internal')]),
    }

    def _default_src_location(self, cr, uid, context=None):
        ids = self.pool.get('stock.warehouse').search(cr, uid, [('code', '=', 'FAB1-INS-ALI')])
        return ids and self.pool.get('stock.warehouse').browse(cr, uid, ids[0]).lot_stock_id.id or False

    def _default_dest_location(self, cr, uid, context=None):
        ids = self.pool.get('stock.warehouse').search(cr, uid, [('code', '=', 'FAB2-ALIM')])
        return ids and self.pool.get('stock.warehouse').browse(cr, uid, ids[0]).lot_stock_id.id or False

    _defaults={
        'location_src_id': _default_src_location,
        'location_dest_id': _default_dest_location,
    }

    def make_mo(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids', []) or []

        obj = self.browse(cr, uid, ids, context)
        context.update({
            'src_location': obj.location_src_id.id,
            'dest_location': obj.location_dest_id.id
        })

        request = self.pool.get('mrp.request.form')
        for record in request.browse(cr, uid, active_ids, context=context):
            if record.state != 'approve':
                raise osv.except_osv(_('Warning!'), _("Selected approved request."))

        request.action_make_mo(cr, uid, active_ids, context)
        return {'type': 'ir.actions.act_window_close'}
