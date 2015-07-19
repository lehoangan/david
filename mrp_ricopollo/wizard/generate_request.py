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

from openerp.osv import osv,fields
from openerp.tools.translate import _
import time

class generate_request(osv.osv_memory):

    _name = "generate.request"

    _columns = {
        'date': fields.date('Fecha de Pedido', required=True),
        'warehouse_ids': fields.many2many('stock.warehouse', 'generate_request_wizard', 'generate_id',
                                          'warehouse_id', 'Código de Granja', domain=[('state', '=', 'open')]),
    }
    _defaults={
        'date': time.strftime('%Y-%m-%d'),
    }

    def action_generate_auto(self, cr, uid, ids=[], context=None):
        new_id = self.create(cr. uid, {'date': time.strftime('%Y-%m-%d')})
        self.action_generate(cr, uid, [new_id])
        return True

    def action_generate(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        sql = '''
            SELECT warehouse.id as warehouse_id, warehouse.capacity, cycle.id as cycle_id, mrp.remain_qty, cycle.date_start,
	            cycle.type, food.product_id
                FROM history_cycle_form cycle
                JOIN stock_warehouse warehouse on (cycle.warehouse_id=warehouse.id)
                JOIN cycle_food_type food on (cycle.id = food.cycle_id)
                JOIN mrp_production mrp on (mrp.location_src_id = warehouse.lot_stock_id)
                WHERE cycle.date_start is not null AND cycle.date_end is null
                AND mrp.state not in ('draft','cancel') AND food.product_id is not null
        '''
        from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
        from datetime import datetime

        standard_obj = self.pool.get('standard.production')
        request_obj = self.pool.get('mrp.request.form')
        request_ids = []

        for obj in self.browse(cr, uid, ids, context):
            warehouse_ids = [ware.id for ware in obj.warehouse_ids]
            if warehouse_ids:
                sql += ' AND warehouse.id in %s '%tuple(warehouse_ids + [-1, -1])
            sql += ''' AND food.date_start <= '%s' AND food.date_end >= '%s' '''%(obj.date, obj.date)
            cr.execute(sql)
            datas = cr.dictfetchall()
            for data in datas:
                age = 0
                date = datetime.strptime(obj.date, DEFAULT_SERVER_DATE_FORMAT)
                date_start = datetime.strptime(data['date_start'], DEFAULT_SERVER_DATE_FORMAT)
                if date > date_start:
                    age = (date - date_start).days
                standard_ids = standard_obj.search(cr, uid, [('type', '=', data['type']), ('date', '=', age)])
                for standard in standard_obj.browse(cr, uid, standard_ids, context):
                    kg = (standard.food_consumption * data['remain_qty'])/1000
                    qq = kg/46
                    request_id = request_obj.create(cr, uid, {
                        'date': obj.date,
                        'warehouse_id': data['warehouse_id'],
                        'cycle_id': data['cycle_id'],
                        'qty_chicken': data['capacity'],
                        'age': age,
                        'product_id': data['product_id'],
                        'qty_qq': qq,
                        'qty_unit': kg,
                        'uom_id': self.pool.get('product.product').browse(cr, uid, data['product_id']).uom_id.id,
                    }, context)
                    request_ids += [request_id]

        return {
            'name': _('New Auto Request'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model':'mrp.request.form',
            'view_id':False,
            'type':'ir.actions.act_window',
            'domain':[('id','in',request_ids)],
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

