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
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp.osv.fields import datetime as datetime_field
from dateutil.relativedelta import relativedelta
from datetime import datetime

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_code_cycle': self.get_code_cycle,
            'get_parent': self.get_parent,
            'get_detail': self.get_detail,
        })

    def get_code_cycle(self, cycle_id):
        return self.pool.get('history.cycle.form').browse(self.cr, self.uid, cycle_id).name

    def _convert_timezone(self, cr, uid, date, plus=True, context={}):
        date = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)

        new_date = datetime_field.context_timestamp(cr, uid,
                                                    timestamp=date,
                                                    context=context)
        new_date = datetime.strptime(new_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT), DEFAULT_SERVER_DATETIME_FORMAT)

        duration = new_date - date
        seconds = duration.total_seconds()
        hours = seconds // 3600
        if plus:
            date = date + relativedelta(hours=hours)
            return date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        else:
            date = date + relativedelta(hours=-hours)
            return date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def get_parent(self, form):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' AND mrp.state not in ('draft', 'cancel', 'done') '''
        else:
            where_str = ''' AND mrp.state = 'done' '''

        if form['date_from']:
            from_date = self._convert_timezone(self.cr, self.uid, form['date_from'] + ' 00:00:00')
            where_str = '%s %s'%(where_str, ''' AND consumed.date >= '%s' '''%from_date)

        if form['date_to']:
            date_to = self._convert_timezone(self.cr, self.uid, form['date_to'] + ' 23:59:59')
            where_str = '%s %s'%(where_str, ''' AND consumed.date <= '%s' '''%date_to)

        if form['food_type_id']:
            where_str = '%s %s'%(where_str, ''' AND mrp.product_id = %s '''%form['food_type_id'][0])

        if form['cycle_id']:
            where_str = '%s %s'%(where_str, ''' AND cl.id = %s '''%form['cycle_id'][0])


        select_str = """
                 SELECT ROW_NUMBER() OVER(ORDER BY min(id)) AS no, min(id) as id, product_id, product,
                    coalesce(sum(consumed_qty),0) as consumed_qty, uom, mrp_no, date,
                    coalesce(sum(waste_qty),0) as waste_qty, coalesce(avg(unit_cost),0) as unit_cost,
                    coalesce(sum(consumed_cost-waste_cost),0) as total_cost, location_id,
                    (SELECT coalesce(sum(total_qty),0) FROM (SELECT CASE WHEN (location_id = tmp.location_id)
                                        THEN sum(-product_uom_qty)
                                        WHEN (location_dest_id = tmp.location_id)
                                        THEN sum(product_uom_qty)
                                        END as total_qty
                                        FROM stock_move
                                        WHERE product_id = tmp.product_id and state = 'done' and id < min(tmp.id)
                                        GROUP BY location_dest_id, location_id) as inventory) as total_qty
                FROM (
                    SELECT
                        min(consumed.id) as id,
                        tmp.name as product,
                        prod.id as product_id,
                        CASE
                        WHEN (location.scrap_location <> TRUE)
                        THEN
                        sum(consumed.product_uom_qty)
                        END as consumed_qty,
                        uom.name as uom,
                        CASE
                        WHEN (location.scrap_location = TRUE)
                        THEN
                        sum(consumed.product_uom_qty)
                        END as waste_qty,
                        avg(consumed.cost_price) as unit_cost,
                        CASE
                        WHEN (location.scrap_location <> TRUE)
                        THEN
                        sum(consumed.product_uom_qty * consumed.cost_price)
                        END as consumed_cost,
                        CASE
                        WHEN (location.scrap_location = TRUE)
                        THEN
                        sum(consumed.product_uom_qty * consumed.cost_price)
                        END as waste_cost,
                        consumed.location_id, mrp.name as mrp_no, consumed.date

                    FROM stock_move consumed
                    JOIN mrp_production mrp on (mrp.id = consumed.raw_material_production_id)
                    JOIN product_product prod on (prod.id = mrp.product_id)
                    JOIN product_template tmp on (tmp.id = prod.product_tmpl_id)
                    JOIN product_uom uom on (uom.id = consumed.product_uom)
                    JOIN stock_location location on (consumed.location_dest_id = location.id)
                    JOIN stock_warehouse warehouse on (mrp.location_src_id = warehouse.lot_stock_id)
                    LEFT JOIN history_cycle_form cl on (cl.warehouse_id=warehouse.id)
                    WHERE consumed.state = 'done' %s
                    GROUP BY tmp.id, tmp.name, uom.name, location.scrap_location, consumed.location_id, prod.id, mrp.name, consumed.date
                ) as tmp
                GROUP BY product_id, product, uom, location_id, mrp_no, date
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()

        result = {}
        no = 1
        for data in res:
            date_tz = self._convert_timezone(self.cr, self.uid, data['date'], True)
            data['date'] = date_tz
            key = (data['mrp_no'], date_tz)

            if key not in result.keys():
                data['no'] = no
                result.update({key: data})
                no += 1
            else:
                result[key]['consumed_qty'] += data['consumed_qty']
                result[key]['waste_qty'] += data['waste_qty']
                result[key]['total_cost'] += data['total_cost']
                result[key]['total_qty'] += data['total_qty']
        return sorted(result.values(), key=lambda k: k['no'])

    def get_detail(self, form, mrp_no, date):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' AND mrp.state not in ('draft', 'cancel', 'done') '''
        else:
            where_str = ''' AND mrp.state = 'done' '''

        if form['date_from']:
            from_date = self._convert_timezone(self.cr, self.uid, form['date_from'] + ' 00:00:00')
            where_str = '%s %s'%(where_str, ''' AND consumed.date >= '%s' '''%from_date)

        if form['date_to']:
            date_to = self._convert_timezone(self.cr, self.uid, form['date_to'] + ' 23:59:59')
            where_str = '%s %s'%(where_str, ''' AND consumed.date <= '%s' '''%date_to)

        if form['cycle_id']:
            where_str = '%s %s'%(where_str, ''' AND cl.id = %s '''%form['cycle_id'][0])

        #get from parent
        if form['food_type_id']:
            where_str = '%s %s'%(where_str, ''' AND mrp.product_id = %s '''%form['food_type_id'][0])
        if mrp_no:
            where_str = '%s %s'%(where_str, ''' AND mrp.name = '%s' '''%mrp_no)


        select_str = """
                 SELECT ROW_NUMBER() OVER(ORDER BY min(id)) AS no, min(id) as id, product_id, product,
                    coalesce(sum(consumed_qty),0) as consumed_qty, uom, mrp_no, date,
                    coalesce(sum(waste_qty),0) as waste_qty, coalesce(avg(unit_cost),0) as unit_cost,
                    coalesce(sum(consumed_cost-waste_cost),0) as total_cost, location_id,
                    (SELECT coalesce(sum(total_qty),0) FROM (SELECT CASE WHEN (location_id = tmp.location_id)
                                        THEN sum(-product_uom_qty)
                                        WHEN (location_dest_id = tmp.location_id)
                                        THEN sum(product_uom_qty)
                                        END as total_qty
                                        FROM stock_move
                                        WHERE product_id = tmp.product_id and state = 'done' and id < min(tmp.id)
                                        GROUP BY location_dest_id, location_id) as inventory) as total_qty
                FROM (
                    SELECT
                        min(consumed.id) as id,
                        tmp.name as product,
                        prod.id as product_id,
                        CASE
                        WHEN (location.scrap_location <> TRUE)
                        THEN
                        sum(consumed.product_uom_qty)
                        END as consumed_qty,
                        uom.name as uom,
                        CASE
                        WHEN (location.scrap_location = TRUE)
                        THEN
                        sum(consumed.product_uom_qty)
                        END as waste_qty,
                        avg(consumed.cost_price) as unit_cost,
                        CASE
                        WHEN (location.scrap_location <> TRUE)
                        THEN
                        sum(consumed.product_uom_qty * consumed.cost_price)
                        END as consumed_cost,
                        CASE
                        WHEN (location.scrap_location = TRUE)
                        THEN
                        sum(consumed.product_uom_qty * consumed.cost_price)
                        END as waste_cost,
                        consumed.location_id, mrp.name as mrp_no, consumed.date

                    FROM stock_move consumed
                    JOIN product_product prod on (prod.id = consumed.product_id)
                    JOIN product_template tmp on (tmp.id = prod.product_tmpl_id)
                    JOIN product_uom uom on (uom.id = consumed.product_uom)
                    JOIN mrp_production mrp on (mrp.id = consumed.raw_material_production_id)
                    JOIN stock_location location on (consumed.location_dest_id = location.id)
                    JOIN stock_warehouse warehouse on (mrp.location_src_id = warehouse.lot_stock_id)
                    LEFT JOIN history_cycle_form cl on (cl.warehouse_id=warehouse.id)
                    WHERE consumed.state = 'done' %s
                    GROUP BY tmp.id, tmp.name, uom.name, location.scrap_location, consumed.location_id, prod.id, mrp.name, consumed.date
                ) as tmp
                GROUP BY product_id, product, uom, location_id, mrp_no, date
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        # print select_str

        result = {}
        no = 1
        for data in res:
            date_tz = self._convert_timezone(self.cr, self.uid, data['date'], True)
            if date_tz != date: continue
            data['date'] = date_tz
            key = (data['product_id'], data['uom'])

            if key not in result.keys():
                data['no'] = no
                result.update({key: data})
                no += 1
            else:
                result[key]['consumed_qty'] += data['consumed_qty']
                result[key]['waste_qty'] += data['waste_qty']
                result[key]['total_cost'] += data['total_cost']
                result[key]['total_qty'] += data['total_qty']
        return sorted(result.values(), key=lambda k: k['no'])

    


