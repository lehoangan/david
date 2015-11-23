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
            'get_parent': self.get_parent,
            'get_detail': self.get_detail,
            'get_total': self.get_total,
            'get_rate': self.get_rate,
            'get_type': self.get_type,
            'get_time': self.get_time,
            'number_of_date': self.number_of_date,
        })
    def get_time(self, a):
        a = str(a)
        asplit = a.split('.')
        return asplit[0] + ':' + str(int(float(asplit[1]) *  0.60))[:2]

    def get_type(self, type):
        dict = {'Male': 'Macho','female': 'Hembra','mixed': 'Mixto'}
        return dict[type]

    def get_rate(self, a, b):
        if a and b:
            return round(float(a) /float(b), 2)
        return 0

    def get_total(self, a, b):
        total = 0
        if a:
            total += float(a)
        if b:
            total -= float(b)
        return total

    def get_parent(self, form):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE sl.state = 'draft' '''
        else:
            where_str = ''' WHERE sl.state not in ('draft', 'cancel') '''

        if form['date']:
            where_str = '%s %s'%(where_str, ''' AND sl.date::date = '%s' '''%form['date'])

        if form['warehouse_id']:
            where_str = '%s %s'%(where_str, ''' AND ware.id = %s '''%form['warehouse_id'][0])

        if form['cycle_id']:
            where_str = '%s %s'%(where_str, ''' AND his.id = %s '''%form['cycle_id'][0])

        if form['slaughtery_id']:
            where_str = '%s %s'%(where_str, ''' AND sl.id = %s '''%form['slaughtery_id'][0])

        select_str = """
                 SELECT his.name as cycle_no, his.id as cycle_id,
                        ware.code as warehouse, ware.id as warehouse_id,
                        ware.capacity,his.date_start,

                        (SELECT sum(dead.total_qty) as total
                            FROM daily_consumption_dead dead
                            JOIN daily_consumption parent on (parent.id = dead.consumption_id)
                            WHERE parent.cycle_id = his.id) as qty_dead,

                        sum(detail.qty) as col5, sum(detail.weight) as col6, 0 as col7, sum(sl.qty_dead) as col8,
                        sum(detail.qty_descarte) as col9, sum(detail.qty_descarte_kg) as col10, sum(processed.qty) as col11,
                        sum(detail.rojas) as col12, sum(detail.rojas_kg) as col13,
                        sum(detail.blancas) as col14, sum(detail.blancas_kg) as col15, sum(detail.rotas) as col16,
                        sum(detail.rotas_kg) as col17

                        FROM slaughtery_chickens_daily sl
                        JOIN stock_warehouse ware on (sl.warehouse_id = ware.id)
                        JOIN history_cycle_form his on (sl.cycle_id = his.id)
                        LEFT JOIN
                        (SELECT SUM(rojas) rojas, SUM(rojas_kg) rojas_kg, SUM(blancas) blancas, SUM(blancas_kg) blancas_kg, SUM(rotas) rotas, SUM(rotas_kg) rotas_kg,
                            SUM(qty + qty_descarte + rojo + pernas_abiertas) qty, SUM(weight + qty_descarte_kg + rotas_kg + pernas_abiertas_kg) weight,
                            SUM(qty_descarte) qty_descarte, SUM(qty_descarte_kg) qty_descarte_kg, slaughtery_id
                        FROM (
                            SELECT avg(qty_rotas_rojas) rojas, avg(qty_rotas_rojas_kg) rojas_kg,
                                        avg(qty_rotas_blancas) blancas, avg(qty_rotas_blancas_kg) blancas_kg,
                                        avg(qty_pernas_rotas) rotas, avg(qty_pernas_rotas_kg) rotas_kg,
                                        avg(qty_rojo) rojo, avg(qty_rojo_kg) rojo_kg, avg(qty_pernas_abiertas) pernas_abiertas, avg(qty_pernas_abiertas_kg) pernas_abiertas_kg,
                                        sum(fdetail.qty) as qty, sum(fdetail.weight) as weight, final.slaughtery_id,
                                        avg(final.qty_descarte) as qty_descarte, avg(final.qty_descarte_kg) as qty_descarte_kg
                                        FROM final_products_for_sale_detail fdetail
                                        JOIN final_products_for_sale final on (fdetail.parent_id = final.id)
                                        GROUP BY final.slaughtery_id, final.id) as final
                                        GROUP BY slaughtery_id) as detail on (detail.slaughtery_id = sl.id)
                        LEFT JOIN
                        (SELECT sum(qty_buchis) as qty,slaughtery_id
                        FROM chicken_is_processed
                        GROUP BY slaughtery_id) as processed on (processed.slaughtery_id = sl.id)

                 %s
                 GROUP BY his.name, his.id,
                        ware.code, ware.id, ware.capacity,his.date_start
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res

    def get_detail(self, form, parent):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE sl.state = 'draft' '''
        else:
            where_str = ''' WHERE sl.state not in ('draft', 'cancel') '''

        if form['date']:
            where_str = '%s %s'%(where_str, ''' AND sl.date::date = '%s' '''%form['date'])

        if form['warehouse_id']:
            where_str = '%s %s'%(where_str, ''' AND ware.id = %s '''%form['warehouse_id'][0])

        if form['cycle_id']:
            where_str = '%s %s'%(where_str, ''' AND his.id = %s '''%form['cycle_id'][0])

        if form['slaughtery_id']:
            where_str = '%s %s'%(where_str, ''' AND sl.id = %s '''%form['slaughtery_id'][0])

        #get from parent
        if parent['cycle_id']:
            where_str = '%s %s'%(where_str, ''' AND his.id = %s '''%parent['cycle_id'])

        if parent['warehouse_id']:
            where_str = '%s %s'%(where_str, ''' AND ware.id = %s '''%parent['warehouse_id'])

        if parent['capacity']:
            where_str = '%s %s'%(where_str, ''' AND ware.capacity = %s '''%parent['capacity'])

        if parent['date_start']:
            where_str = '%s %s'%(where_str, ''' AND his.date_start = '%s' '''%parent['date_start'])

        select_str = """
                 SELECT sl.id, his.name as cycle_no, his.date_start as date_start, ware.name as warehouse, ware.capacity,
                    his.date_start, sl.name as col1, sl.date as col2, sl.time as col3, his.type as col4,
                    detail.qty as col5, detail.weight as col6, 0 as col7, sl.qty_dead as col8,
                    detail.qty_descarte as col9, detail.qty_descarte_kg as col10, processed.qty as col11, detail.rojas as col12, detail.rojas_kg as col13,
                    detail.blancas as col14, detail.blancas_kg as col15, detail.rotas as col16, detail.rotas_kg as col17
                    FROM slaughtery_chickens_daily sl
                    JOIN stock_warehouse ware on (sl.warehouse_id = ware.id)
                    JOIN history_cycle_form his on (sl.cycle_id = his.id)

                    LEFT JOIN
                        (SELECT SUM(rojas) rojas, SUM(rojas_kg) rojas_kg, SUM(blancas) blancas, SUM(blancas_kg) blancas_kg, SUM(rotas) rotas, SUM(rotas_kg) rotas_kg,
                            SUM(qty + qty_descarte + rojo + pernas_abiertas) qty, SUM(weight + qty_descarte_kg + rotas_kg + pernas_abiertas_kg) weight,
                            SUM(qty_descarte) qty_descarte, SUM(qty_descarte_kg) qty_descarte_kg, slaughtery_id
                        FROM (
                            SELECT avg(qty_rotas_rojas) rojas, avg(qty_rotas_rojas_kg) rojas_kg,
                                        avg(qty_rotas_blancas) blancas, avg(qty_rotas_blancas_kg) blancas_kg,
                                        avg(qty_pernas_rotas) rotas, avg(qty_pernas_rotas_kg) rotas_kg,
                                        avg(qty_rojo) rojo, avg(qty_rojo_kg) rojo_kg, avg(qty_pernas_abiertas) pernas_abiertas, avg(qty_pernas_abiertas_kg) pernas_abiertas_kg,
                                        sum(fdetail.qty) as qty, sum(fdetail.weight) as weight, final.slaughtery_id,
                                        avg(final.qty_descarte) as qty_descarte, avg(final.qty_descarte_kg) as qty_descarte_kg
                                        FROM final_products_for_sale_detail fdetail
                                        JOIN final_products_for_sale final on (fdetail.parent_id = final.id)
                                        GROUP BY final.slaughtery_id, final.id) as final
                                        GROUP BY slaughtery_id) as detail on (detail.slaughtery_id = sl.id)
                    LEFT JOIN
                        (SELECT sum(qty_buchis) as qty,slaughtery_id
                        FROM chicken_is_processed
                        GROUP BY slaughtery_id) as processed on (processed.slaughtery_id = sl.id)
                %s
                ORDER BY sl.name
        """%where_str

        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res

    def number_of_date(self, date, date2):
        from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
        from datetime import datetime
        if not date or not date2:
            return 0
        date = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
        date2 = datetime.strptime(date2, DEFAULT_SERVER_DATE_FORMAT)
        day = (date2 - date).days
        return day


    


