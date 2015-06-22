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
from openerp.tools.translate import _

class product_product(osv.Model):

    _inherit = "product.product"
    
    def write(self, cr, uid, ids, vals, context=None):
        if self.pool['res.users'].has_group(cr, uid, 'base.not_create_and_edit_product'):
            raise openerp.exceptions.AccessError(_("You is not allowed for edit or create"))
        return super(product_product, self).write(cr, uid, ids, vals, context)

    def create(self, cr, uid, vals, context=None):
        if self.pool['res.users'].has_group(cr, uid, 'base.not_create_and_edit_product'):
            raise openerp.exceptions.AccessError(_("You is not allowed for edit or create"))
        return super(product_product, self).create(cr, uid, vals, context)

class product_template(osv.Model):
    _inherit = 'product.template'

    def write(self, cr, uid, ids, vals, context=None):
        if self.pool['res.users'].has_group(cr, uid, 'base.not_create_and_edit_product'):
            raise openerp.exceptions.AccessError(_("You is not allowed for edit or create"))
        return super(product_template, self).write(cr, uid, ids, vals, context)

class product_uom(osv.osv):
    _inherit = 'product.uom'

    def write(self, cr, uid, ids, vals, context=None):
        if self.pool['res.users'].has_group(cr, uid, 'base.allow_create_edit_delete_uom'):
            return super(product_uom, self).write(cr, uid, ids, vals, context)
        raise openerp.exceptions.AccessError(_("You is not allowed for edit or create"))

    def create(self, cr, uid, vals, context=None):
        if self.pool['res.users'].has_group(cr, uid, 'base.allow_create_edit_delete_uom'):
            return super(product_uom, self).create(cr, uid, vals, context)
        raise openerp.exceptions.AccessError(_("You is not allowed for edit or create"))

    def unlink(self, cr, uid, ids, context=None):
        if self.pool['res.users'].has_group(cr, uid, 'base.allow_create_edit_delete_uom'):
            return super(product_uom, self).unlink(cr, uid, ids, context)
        raise openerp.exceptions.AccessError(_("You is not allowed for edit or create"))
