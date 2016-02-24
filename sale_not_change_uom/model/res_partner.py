# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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


import openerp
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID, api
from openerp.tools.translate import _

class res_partner(osv.Model):

    _inherit = "res.partner"

    _columns = {
        'frial': fields.boolean('Frial Rico Pollo'),
        'warning_invoice': fields.integer('Aviso de Límite de Boletas'),
        'collected_journal_id': fields.many2one('account.journal', 'Collector Journal'),
        'sale_journal_id': fields.many2one('account.journal', 'Sale Journal', domain="[('type','=','sale')]"),
        'purchase_journal_id': fields.many2one('account.journal', 'Purchase Journal', domain="[('type','=','purchase')]"),
        'r_type': fields.selection([('A', 'A'), ('B', 'B'), ('C', 'C'), ('X', 'X')], 'Tipo Cliente'),
        }
    
    @api.multi
    def write(self, vals):
        if (vals.get('customer', False) or self.customer) and \
                self.env['res.users'].has_group('base.not_create_and_edit_customer'):
            raise openerp.exceptions.AccessError(_("You is not allowed for edit or create"))

        if (vals.get('supplier', False) or self.supplier) and \
                self.env['res.users'].has_group('base.not_create_and_edit_supplier'):
            raise openerp.exceptions.AccessError(_("You is not allowed for edit or create"))
        return super(res_partner, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get('customer', False) and \
                self.env['res.users'].has_group('base.not_create_and_edit_customer'):
            raise openerp.exceptions.AccessError(_("You is not allowed for edit or create"))

        if vals.get('supplier', False) and \
                self.env['res.users'].has_group('base.not_create_and_edit_supplier'):
            raise openerp.exceptions.AccessError(_("You is not allowed for edit or create"))
        return super(res_partner, self).create(vals)
