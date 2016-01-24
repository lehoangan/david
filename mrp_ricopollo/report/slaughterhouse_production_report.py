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
            'lines': self._get_lines,
            'lines2': self._get_lines2,
            'sums': self._get_lines_sum,
            'sums2': self._get_lines2_sum,
        })
    def _get_lines(self, form):
        where_1 = 'WHERE 1=1 '
        if form['date_from']:
            where_1 = '%s %s'%(where_1, ''' AND slaughtery.date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_1 = '%s %s'%(where_1, ''' AND slaughtery.date <= '%s' '''%form['date_to'])

        where_2 = ''
        if form['date_from']:
            where_2 = '%s %s'%(where_2, ''' AND s.date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_2 = '%s %s'%(where_2, ''' AND s.date <= '%s' '''%form['date_to'])

        select_str = """
                 SELECT ROW_NUMBER() OVER(ORDER BY date) AS no, * FROM
                        (SELECT ROW_NUMBER() OVER(ORDER BY date) AS no, date, SUM(col2) as col2, SUM(col3) as col3,COALESCE(SUM(col5), 0) as col5, COALESCE(SUM(col6), 0) as col6,
                    COALESCE(SUM(col8), 0) as col8, COALESCE(SUM(col9), 0) as col9, COALESCE(SUM(col11), 0) as col11, COALESCE(SUM(col12), 0) as col12
                    FROM (
                    SELECT slaughtery.id, slaughtery.date, COALESCE(SUM(qty_qq), 0) as col2, COALESCE(SUM(qty_kg), 0) as col3, COALESCE(SUM(final.qty), 0) as col5,
                        COALESCE(SUM(final.weight), 0) as col6,
                        COALESCE(SUM(final.qty - qty_qq), 0) as col8,COALESCE(SUM(final.weight - qty_kg), 0) as col9,
                        COALESCE(SUM(final_part.qty), 0) as col11, COALESCE(SUM(final_part.weight), 0) as col12
                                            FROM slaughtery_chickens_daily slaughtery
                                            LEFT JOIN (SELECT SUM(qty + qty_descarte + rojo + pernas_abiertas) qty, SUM(weight + qty_descarte_kg + rojo_kg + pernas_abiertas_kg) weight, slaughtery_id
                                                FROM (
                                                    SELECT      avg(qty_rojo) rojo, avg(qty_rojo_kg) rojo_kg, avg(qty_pernas_abiertas) pernas_abiertas, avg(qty_pernas_abiertas_kg) pernas_abiertas_kg,
                                                        sum(fdetail.qty) as qty, sum(fdetail.weight) as weight, final.slaughtery_id,
                                                        avg(final.qty_descarte) as qty_descarte, avg(final.qty_descarte_kg) as qty_descarte_kg
                                                        FROM final_products_for_sale final
                                                        LEFT JOIN final_products_for_sale_detail fdetail on (fdetail.parent_id = final.id)
                                                        LEFT JOIN product_product prod on (fdetail.product_id = prod.id)
                                                        LEFT JOIN product_template tmp on (tmp.id = prod.product_tmpl_id)
                                                        WHERE (tmp.name like 'Pollo Entero' or tmp.name like 'Pi. (P. Entero)') and final.state = 'confirm'
                                                        GROUP BY final.slaughtery_id, final.id) as final
                                                        GROUP BY slaughtery_id) as final on (final.slaughtery_id = slaughtery.id)
                                            LEFT JOIN (SELECT
                                                sum(fdetail.qty) as qty, sum(fdetail.weight) as weight, final.slaughtery_id
                                                FROM final_part_of_product final
                                                LEFT JOIN final_part_of_product_finish_detail fdetail on (fdetail.parent_finish_id = final.id)
                                                WHERE state = 'confirm'
                                                GROUP BY final.slaughtery_id) as final_part on (final_part.slaughtery_id = slaughtery.id)
                                            %s
                                             GROUP BY slaughtery.date, slaughtery.id) as aaa GROUP BY date) as sql01

                        LEFT JOIN
                        (SELECT sum(l.product_uos_qty) as col14,
                                           sum(l.product_uom_qty) as col15,
                                           sum(l.discount_kg) as disc_kg,
                                           s.date as so_date
                                    FROM sale_order_line l
                                    JOIN sale_order s on (l.order_id=s.id)
                                    LEFT JOIN product_product prod on (l.product_id = prod.id)
                                    LEFT JOIN product_template tmp on (tmp.id = prod.product_tmpl_id)
                                    WHERE (tmp.name like 'Pollo Entero' or tmp.name like 'Pi. (P. Entero)') AND s.state not in ('draft', 'confirm')
                                    %s
                                    GROUP BY s.date)as sql02 ON (sql01.date = sql02.so_date)

        """%(where_1, where_2)
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res

    def _get_lines_sum(self, form):
        where_1 = 'WHERE 1=1 '
        if form['date_from']:
            where_1 = '%s %s'%(where_1, ''' AND slaughtery.date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_1 = '%s %s'%(where_1, ''' AND slaughtery.date <= '%s' '''%form['date_to'])

        where_2 = ''
        if form['date_from']:
            where_2 = '%s %s'%(where_2, ''' AND s.date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_2 = '%s %s'%(where_2, ''' AND s.date <= '%s' '''%form['date_to'])

        select_str = """
                 SELECT SUM(col2) as col2, SUM(col3) as col3, SUM(col5) as col5, SUM(col6) as col6,
                    SUM(col8) as col8, SUM(col9) as col9, SUM(col11) as col11, SUM(col12) as col12 , SUM(col14) as col14,
                    SUM(col15) as col15, SUM(disc_kg) as disc_kg
                    FROM (
                        (SELECT ROW_NUMBER() OVER(ORDER BY date) AS no, date, SUM(col2) as col2, SUM(col3) as col3,COALESCE(SUM(col5), 0) as col5, COALESCE(SUM(col6), 0) as col6,
                    COALESCE(SUM(col8), 0) as col8, COALESCE(SUM(col9), 0) as col9, COALESCE(SUM(col11), 0) as col11, COALESCE(SUM(col12), 0) as col12
                    FROM (
                    SELECT slaughtery.id, slaughtery.date, COALESCE(SUM(qty_qq), 0) as col2, COALESCE(SUM(qty_kg), 0) as col3, COALESCE(SUM(final.qty), 0) as col5,
                        COALESCE(SUM(final.weight), 0) as col6,
                        COALESCE(SUM(final.qty - qty_qq), 0) as col8,COALESCE(SUM(final.weight - qty_kg), 0) as col9,
                        COALESCE(SUM(final_part.qty), 0) as col11, COALESCE(SUM(final_part.weight), 0) as col12
                                            FROM slaughtery_chickens_daily slaughtery
                                            LEFT JOIN (SELECT SUM(qty + qty_descarte + rojo + pernas_abiertas) qty, SUM(weight + qty_descarte_kg + rojo_kg + pernas_abiertas_kg) weight, slaughtery_id
                                                FROM (
                                                    SELECT      avg(qty_rojo) rojo, avg(qty_rojo_kg) rojo_kg, avg(qty_pernas_abiertas) pernas_abiertas, avg(qty_pernas_abiertas_kg) pernas_abiertas_kg,
                                                        sum(fdetail.qty) as qty, sum(fdetail.weight) as weight, final.slaughtery_id,
                                                        avg(final.qty_descarte) as qty_descarte, avg(final.qty_descarte_kg) as qty_descarte_kg
                                                        FROM final_products_for_sale final
                                                        LEFT JOIN final_products_for_sale_detail fdetail on (fdetail.parent_id = final.id)
                                                        LEFT JOIN product_product prod on (fdetail.product_id = prod.id)
                                                        LEFT JOIN product_template tmp on (tmp.id = prod.product_tmpl_id)
                                                        WHERE (tmp.name like 'Pollo Entero' or tmp.name like 'Pi. (P. Entero)') and final.state = 'confirm'
                                                        GROUP BY final.slaughtery_id, final.id) as final
                                                        GROUP BY slaughtery_id) as final on (final.slaughtery_id = slaughtery.id)
                                            LEFT JOIN (SELECT
                                                sum(fdetail.qty) as qty, sum(fdetail.weight) as weight, final.slaughtery_id
                                                FROM final_part_of_product final
                                                LEFT JOIN final_part_of_product_finish_detail fdetail on (fdetail.parent_finish_id = final.id)
                                                WHERE state = 'confirm'
                                                GROUP BY final.slaughtery_id) as final_part on (final_part.slaughtery_id = slaughtery.id)
                                            %s
                                             GROUP BY slaughtery.date, slaughtery.id) as aaa GROUP BY date) as sql01

                        LEFT JOIN
                        (SELECT sum(l.product_uos_qty) as col14,
                                           sum(l.product_uom_qty) as col15,
                                           sum(l.discount_kg) as disc_kg,
                                           s.date as so_date
                                    FROM sale_order_line l
                                    JOIN sale_order s on (l.order_id=s.id)
                                    LEFT JOIN product_product prod on (l.product_id = prod.id)
                                    LEFT JOIN product_template tmp on (tmp.id = prod.product_tmpl_id)
                                    WHERE (tmp.name like 'Pollo Entero' or tmp.name like 'Pi. (P. Entero)') AND s.state not in ('draft', 'confirm')
                                    %s
                                    GROUP BY s.date)as sql02 ON (sql01.date = sql02.so_date)) as aa

        """%(where_1, where_2)
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res

    def _get_lines2(self, form):
        where_1 = 'WHERE 1=1 '
        if form['date_from']:
            where_1 = '%s %s'%(where_1, ''' AND slaughtery.date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_1 = '%s %s'%(where_1, ''' AND slaughtery.date <= '%s' '''%form['date_to'])

        select_str = """
                 SELECT ROW_NUMBER() OVER(ORDER BY date) AS no, date, SUM(col2) as col2, SUM(col3) as col3,COALESCE(SUM(col20), 0) as col20, COALESCE(SUM(col21), 0) as col21, COALESCE(SUM(col22), 0) as col22,
                    COALESCE(SUM(col24), 0) as col24, COALESCE(SUM(col26), 0) as col26, COALESCE(SUM(col27), 0) as col27,
                    COALESCE(SUM(col29), 0) as col29, COALESCE(SUM(col30), 0) as col30,
                    COALESCE(SUM(col32), 0) as col32, COALESCE(SUM(col33), 0) as col33
FROM (
SELECT slaughtery.id, slaughtery.date, COALESCE(avg(slaughtery.qty_qq), 0) as col2, COALESCE(avg(slaughtery.qty_kg), 0) as col3, COALESCE(SUM(rojo), 0) as col20, COALESCE(SUM(qty_descarte), 0) as col21, COALESCE(SUM(qty_descarte_kg), 0) as col22,
                    COALESCE(SUM(qty_buchis), 0) as col24, COALESCE(SUM(col26), 0) as col26, COALESCE(SUM(col27), 0) as col27,
                    COALESCE(SUM(qty_pernas_rotas), 0) as col29, COALESCE(SUM(qty_pernas_rotas_kg), 0) as col30,
                    COALESCE(SUM(qty_pernas_abiertas), 0) as col32, COALESCE(SUM(qty_pernas_abiertas_kg), 0) as col33
                    FROM slaughtery_chickens_daily slaughtery
                    LEFT JOIN chicken_is_processed proccessed on (proccessed.slaughtery_id = slaughtery.id)
                    LEFT JOIN (
                    SELECT SUM(rojo) rojo, SUM(qty_descarte) qty_descarte, SUM(qty_descarte_kg) qty_descarte_kg, slaughtery_id,
                        SUM(qty_rotas_blancas+qty_rotas_rojas) col26,SUM(qty_rotas_blancas_kg+qty_rotas_rojas_kg) col27,
                        SUM(qty_pernas_rotas) qty_pernas_rotas, SUM(qty_pernas_rotas_kg) qty_pernas_rotas_kg,
                        SUM(qty_pernas_abiertas) qty_pernas_abiertas,SUM(qty_pernas_abiertas_kg) qty_pernas_abiertas_kg
                    FROM (
                        SELECT avg(qty_rojo) rojo, avg(qty_rojo_kg) rojo_kg, avg(qty_pernas_abiertas) pernas_abiertas,
                        avg(qty_pernas_abiertas_kg) pernas_abiertas_kg,avg(qty_rotas_rojas) qty_rotas_rojas,avg(qty_rotas_blancas) qty_rotas_blancas,
                        avg(qty_rotas_blancas_kg) qty_rotas_blancas_kg,avg(qty_rotas_rojas_kg) qty_rotas_rojas_kg,
                        avg(qty_pernas_rotas) qty_pernas_rotas,avg(qty_pernas_rotas_kg) qty_pernas_rotas_kg,
                        avg(qty_pernas_abiertas) qty_pernas_abiertas,avg(qty_pernas_abiertas_kg) qty_pernas_abiertas_kg,
                        sum(fdetail.qty) as qty, sum(fdetail.weight) as weight, final.slaughtery_id,
                        avg(final.qty_descarte) as qty_descarte, avg(final.qty_descarte_kg) as qty_descarte_kg
                        FROM final_products_for_sale final
                        LEFT JOIN final_products_for_sale_detail fdetail on (fdetail.parent_id = final.id)
                        LEFT JOIN product_product prod on (fdetail.product_id = prod.id)
                        LEFT JOIN product_template tmp on (tmp.id = prod.product_tmpl_id)
                        WHERE (tmp.name like 'Pollo Entero' or tmp.name like 'Pi. (P. Entero)') and final.state = 'confirm'
                        GROUP BY final.slaughtery_id, final.id) as final
                        GROUP BY slaughtery_id) as final on (final.slaughtery_id = slaughtery.id)
                    LEFT JOIN (SELECT
                    sum(fdetail.qty) as qty, sum(fdetail.weight) as weight, final.slaughtery_id
                    FROM final_part_of_product final
                    LEFT JOIN final_part_of_product_finish_detail fdetail on (fdetail.parent_finish_id = final.id)
                    WHERE state = 'confirm'
                    GROUP BY final.slaughtery_id) as final_part on (final_part.slaughtery_id = slaughtery.id)
                    %s
                    GROUP BY slaughtery.date, slaughtery.id) as aaa GROUP BY date

        """%where_1
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res

    def _get_lines2_sum(self, form):
        where_1 = 'WHERE 1=1 '
        if form['date_from']:
            where_1 = '%s %s'%(where_1, ''' AND slaughtery.date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_1 = '%s %s'%(where_1, ''' AND slaughtery.date <= '%s' '''%form['date_to'])

        select_str = """
            SELECT SUM(col2) col2,SUM(col3) col3,SUM(col20) col20,SUM(col21) col21,SUM(col22) col22,SUM(col24) col24,SUM(col26) col26,SUM(col27) col27,
                  SUM(col30) col30,SUM(col32) col32,SUM(col33) col33,SUM(col29) col29
            FROM (
                 SELECT ROW_NUMBER() OVER(ORDER BY date) AS no, date, SUM(col2) as col2, SUM(col3) as col3,COALESCE(SUM(col20), 0) as col20, COALESCE(SUM(col21), 0) as col21, COALESCE(SUM(col22), 0) as col22,
                    COALESCE(SUM(col24), 0) as col24, COALESCE(SUM(col26), 0) as col26, COALESCE(SUM(col27), 0) as col27,
                    COALESCE(SUM(col29), 0) as col29, COALESCE(SUM(col30), 0) as col30,
                    COALESCE(SUM(col32), 0) as col32, COALESCE(SUM(col33), 0) as col33
FROM (
SELECT slaughtery.id, slaughtery.date, COALESCE(avg(slaughtery.qty_qq), 0) as col2, COALESCE(avg(slaughtery.qty_kg), 0) as col3, COALESCE(SUM(rojo), 0) as col20, COALESCE(SUM(qty_descarte), 0) as col21, COALESCE(SUM(qty_descarte_kg), 0) as col22,
                    COALESCE(SUM(qty_buchis), 0) as col24, COALESCE(SUM(col26), 0) as col26, COALESCE(SUM(col27), 0) as col27,
                    COALESCE(SUM(qty_pernas_rotas), 0) as col29, COALESCE(SUM(qty_pernas_rotas_kg), 0) as col30,
                    COALESCE(SUM(qty_pernas_abiertas), 0) as col32, COALESCE(SUM(qty_pernas_abiertas_kg), 0) as col33
                    FROM slaughtery_chickens_daily slaughtery
                    LEFT JOIN chicken_is_processed proccessed on (proccessed.slaughtery_id = slaughtery.id)
                    LEFT JOIN (
                    SELECT SUM(rojo) rojo, SUM(qty_descarte) qty_descarte, SUM(qty_descarte_kg) qty_descarte_kg, slaughtery_id,
                        SUM(qty_rotas_blancas+qty_rotas_rojas) col26,SUM(qty_rotas_blancas_kg+qty_rotas_rojas_kg) col27,
                        SUM(qty_pernas_rotas) qty_pernas_rotas, SUM(qty_pernas_rotas_kg) qty_pernas_rotas_kg,
                        SUM(qty_pernas_abiertas) qty_pernas_abiertas,SUM(qty_pernas_abiertas_kg) qty_pernas_abiertas_kg
                    FROM (
                        SELECT avg(qty_rojo) rojo, avg(qty_rojo_kg) rojo_kg, avg(qty_pernas_abiertas) pernas_abiertas,
                        avg(qty_pernas_abiertas_kg) pernas_abiertas_kg,avg(qty_rotas_rojas) qty_rotas_rojas,avg(qty_rotas_blancas) qty_rotas_blancas,
                        avg(qty_rotas_blancas_kg) qty_rotas_blancas_kg,avg(qty_rotas_rojas_kg) qty_rotas_rojas_kg,
                        avg(qty_pernas_rotas) qty_pernas_rotas,avg(qty_pernas_rotas_kg) qty_pernas_rotas_kg,
                        avg(qty_pernas_abiertas) qty_pernas_abiertas,avg(qty_pernas_abiertas_kg) qty_pernas_abiertas_kg,
                        sum(fdetail.qty) as qty, sum(fdetail.weight) as weight, final.slaughtery_id,
                        avg(final.qty_descarte) as qty_descarte, avg(final.qty_descarte_kg) as qty_descarte_kg
                        FROM final_products_for_sale final
                        LEFT JOIN final_products_for_sale_detail fdetail on (fdetail.parent_id = final.id)
                        LEFT JOIN product_product prod on (fdetail.product_id = prod.id)
                        LEFT JOIN product_template tmp on (tmp.id = prod.product_tmpl_id)
                        WHERE (tmp.name like 'Pollo Entero' or tmp.name like 'Pi. (P. Entero)') and final.state = 'confirm'
                        GROUP BY final.slaughtery_id, final.id) as final
                        GROUP BY slaughtery_id) as final on (final.slaughtery_id = slaughtery.id)
                    LEFT JOIN (SELECT
                    sum(fdetail.qty) as qty, sum(fdetail.weight) as weight, final.slaughtery_id
                    FROM final_part_of_product final
                    LEFT JOIN final_part_of_product_finish_detail fdetail on (fdetail.parent_finish_id = final.id)
                    WHERE state = 'confirm'
                    GROUP BY final.slaughtery_id) as final_part on (final_part.slaughtery_id = slaughtery.id)
                    %s
                    GROUP BY slaughtery.date, slaughtery.id) as aaa GROUP BY date) as aa

        """%where_1
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res



    


