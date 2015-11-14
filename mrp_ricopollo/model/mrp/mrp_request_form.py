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

class mrp_request_form(osv.osv):
    _name = 'mrp.request.form'
    _inherit = ['mail.thread']

    _columns ={        
        'name': fields.char('Ref', 100, readonly=True, states={'draft': [('readonly', False)]}),
        'description': fields.char('Notas', 100, readonly=True, states={'draft': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', 'Create By', readonly=True),

        'date': fields.date('Fecha de Pedido', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'warehouse_id': fields.many2one('stock.warehouse', 'Código de Granja', required=True,
                                        domain=[('state', '=', 'open')],
                                        readonly=True, states={'draft': [('readonly', False)]}),
        'cycle_id': fields.many2one('history.cycle.form', 'Ciclo', required=True,
                                        domain="[('warehouse_id', '=', warehouse_id), ('date_end', '=', False)]",
                                        readonly=True, states={'draft': [('readonly', False)]}),
        'qty_chicken': fields.float('Capacidad Pollos', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'cycle_start_date': fields.related('cycle_id', 'date_start', string='Fecha Inicio', type='date', readonly=True),
        'age': fields.integer('Age', readonly=True, states={'draft': [('readonly', False)]}),

        #product detail
        'product_id': fields.many2one('product.product', 'Tipo Alimento', domain="[('bom_ids','!=',False),('bom_ids.type','!=','phantom')]", required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'qty_qq': fields.float('Cantidad (qq)', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'qty_unit': fields.float('Kilogramos', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'uom_id': fields.many2one('product.uom', 'UoM', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Borrador'),
            ('approve', 'Aprobar'),
            ('cancel', 'Cancelar'),
            ('mo', 'MO Created'),
            ], 'Status', select=True),
    }

    _defaults= {
        'state': 'draft',
        'user_id': lambda self,cr,uid,context=None: uid,
        'date': time.strftime('%Y-%m-%d'),
    }


    def onchange_age(self, cr, uid, ids, date, cycle_id, context=None):
        if not date or not cycle_id:
            return {'value': {}}
        from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
        from datetime import datetime

        date = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
        cycle = self.pool.get('history.cycle.form').browse(cr, uid, cycle_id, context)
        date_start = datetime.strptime(cycle.date_start, DEFAULT_SERVER_DATE_FORMAT)
        if date > date_start:
            return {'value': {'age': (date - date_start).days}}
        return  {'value': {'age': 0}}

    def onchange_warehouse_id(self, cr, uid, ids, warehouse_id, context=None):
        if not warehouse_id:
            return {'value': {'qty_chicken': 0}}
        warehouse = self.pool.get('stock.warehouse').browse(cr, uid, warehouse_id)
        return {'value': {'qty_chicken': warehouse.capacity}}

    def onchange_product_id(self, cr, uid, ids, product_id, qty_qq, context=None):
        if product_id:
            prod_obj = self.pool.get('product.product').browse(cr, uid, product_id, context)
            uom_id = prod_obj.uom_id.id
            qty_unit = qty_qq * 46
            return {'value': {'product_id': product_id,
                              'qty_qq': qty_qq,
                              'qty_unit': qty_unit,
                              'uom_id': uom_id}}
        return {'value': {'product_id': False,
                          'qty_qq': 0,
                          'qty_unit': 0,
                          'uom_id': False}}

    def action_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel',})

    def action_set_to_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft',})
    def action_approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'approve'})
    
    def action_make_mo(self, cr, uid, ids, context=None):
        production_obj = self.pool.get('mrp.production')
        bom_obj = self.pool.get('mrp.bom')
        product_uom_obj = self.pool.get('product.uom')
        dict_product = {}
        warehouse_id = False
        for obj in self.browse(cr, uid, ids, context):
            if not warehouse_id:
                warehouse_id = obj.warehouse_id
            elif warehouse_id != obj.warehouse_id:
                raise osv.except_osv(_("Invalid Action!"), _("Selected the same receive place."))

            q = product_uom_obj._compute_qty(cr, uid, obj.uom_id.id, obj.qty_unit, obj.product_id.uom_id.id)
            name = '%s:%s'%(obj.name, obj.description)
            if obj.product_id.id not in dict_product.keys():
                dict_product.update({obj.product_id.id: [q, [name], obj.product_id.uom_id.id]})
            else:
                dict_product[obj.product_id.id][0] += q
                if name not in dict_product[obj.product_id.id][1]:
                    dict_product[obj.product_id.id][1] += [name]
        for product_id in dict_product.keys():
            bom_id = bom_obj._bom_find(cr, uid, product_id=product_id,
                                                    properties=[], context=context)
            if bom_id:
                bom = bom_obj.browse(cr, uid, bom_id, context=context)
                routing_id = bom.routing_id.id
                produce_id = production_obj.create(cr, uid, {
                    'origin': ','.join([str(x) for x in dict_product[product_id][1]]),
                    'product_id': product_id,
                    'product_qty': dict_product[product_id][0],
                    'product_uom': dict_product[product_id][2],
                    'location_src_id': warehouse_id.lot_stock_id.id,
                    'location_dest_id': warehouse_id.lot_stock_id.id,
                    'bom_id': bom_id,
                    'routing_id': routing_id,
                    'date_planned': time.strftime('%Y-%m-%d %H:%M:%S'),
                })
            else:
                raise osv.except_osv(_('Invalid Action!'), _('No BOM found for %s.')%self.pool.get('product.product').browse(cr, uid, product_id).name)

        return self.write(cr, uid, ids, {'state': 'mo'})
