##############################################################################
#
# Copyright (c) 2008-2011 Alistek Ltd (http://www.alistek.com) All Rights Reserved.
#                    General contacts <info@alistek.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This module is GPLv3 or newer and incompatible
# with OpenERP SA "AGPL + Private Use License"!
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.report import report_sxw

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_detail': self.get_detail,
        })

    def location(self, lot_id):
        res = self.pool.get('stock.location').name_get(self.cr, self.uid, [lot_id])
        return res and res[0] and res[0][1] or self.pool.get('stock.location').browse(self.cr, self.uid, lot_id).name
    
    def get_detail(self, form):
        cr, uid = self.cr, self.uid
        sql = """
                 SELECT ROW_NUMBER() OVER(ORDER BY warehouse.id) AS no, warehouse.code,
                    cl.name as cl_no, mrp.remain_qty as qty_chitken,
                    CASE WHEN (cl.type = 'Male')
                    THEN 'Macho'
                    WHEN (cl.type = 'female')
                    THEN 'Hembra'
                    WHEN (cl.type = 'mixed')
                    THEN 'Mixto'
                    END as type ,
                    cl.type as origin_type,
                    tmp.name,
                    food.date_start,
                    food.date_end,
                    prod.id as prod_id,
                    cl.id as cycle_id

                    FROM stock_warehouse warehouse
                    JOIN mrp_production mrp on (mrp.location_src_id = warehouse.lot_stock_id)
                    LEFT JOIN history_cycle_form cl on (cl.warehouse_id=warehouse.id)
                    LEFT JOIN cycle_food_type food on (food.cycle_id= cl.id)
                    LEFT JOIN product_product prod on (food.product_id= prod.id)
                    LEFT JOIN product_template tmp on (prod.product_tmpl_id= tmp.id)
                WHERE cl.date_start is not null AND food.product_id is not null
        """
        from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
        from datetime import datetime

        standard_obj = self.pool.get('standard.production')
        consumption_obj = self.pool.get('daily.consumption.material')

        warehouse_id = form['warehouse_id'][0] or False
        if warehouse_id:
            sql += ' AND warehouse.id = %s '%warehouse_id
        if form['year']:
            sql += ''' AND date_part('year', mrp.date_planned) = %s '''%form['year']
        if form['type'] == 'active':
            sql += '  AND cl.date_end is null '
        else:
            sql += '  AND cl.date_end is not null '
        cr.execute(sql)
        datas = cr.dictfetchall()
        for data in datas:
            kg = 0
            if form['type'] == 'active':
                age = 0
                date_end = datetime.strptime(data['date_end'], DEFAULT_SERVER_DATE_FORMAT)
                date_start = datetime.strptime(data['date_start'], DEFAULT_SERVER_DATE_FORMAT)
                if date_end > date_start:
                    age = (date_end - date_start).days
                standard_ids = standard_obj.search(cr, uid, [('type', '=', data['origin_type']), ('date', '<=', age)])

                for standard in standard_obj.browse(cr, uid, standard_ids):
                    kg += (standard.food_consumption * data['qty_chitken'])/1000

            else:
                consumption_ids = consumption_obj.search(cr, uid, [('product_id', '=', data['prod_id']),
                                                                   ('consumption_id.cycle_id', '=', data['cycle_id']),
                                                                   ('consumption_id.date', '>=', data['date_start']),
                                                                   ('consumption_id.date', '<=', data['date_end']),])

                for consumption in consumption_obj.browse(cr, uid, consumption_ids):
                    kg += consumption.quantity
            data.update({'qq': kg/46,
                         'kg': kg})
        return datas
