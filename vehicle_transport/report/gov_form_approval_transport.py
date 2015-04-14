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
            'get_total_detail': self.get_total_detail,
            'get_total' : self.get_total,
            'get_vehicle' : self.get_vehicle,
        })
    def get_vehicle(self, form):
        where_str = ''' WHERE s.state = 'draft' '''

        if form['driver_id']:
            where_str = '%s %s'%(where_str, ' AND vehicle.driver_id = %s'%form['driver_id'][0])

        if form['date']:
            where_str = '%s %s'%(where_str, ''' AND s.date_order::date = '%s' '''%form['date'])

        if form['market_id']:
            where_str = '%s %s'%(where_str, ''' AND categ.id = %s '''%form['market_id'][0])

        select_str = """
              SELECT
                        vehicle.driver_license, vehicle.license_plate, vehicle.color
                FROM (
                    sale_order_line l
                          join sale_order s on (l.order_id=s.id)
                          join res_partner part on (s.partner_id=part.id)
                          join fleet_vehicle vehicle on (s.vehicle_id=vehicle.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id)
                            left join product_product p on (l.product_id=p.id)
                                left join product_template t on (p.product_tmpl_id=t.id)
                        left join product_uom u on (u.id=l.product_uom)
                        left join product_uom u2 on (u2.id=t.uom_id))
                %s
              limit 1
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res

    def get_total(self, form):
        where_str = ''' WHERE s.state = 'draft' AND l.product_uos is not null '''
        
        if form['driver_id']:
            where_str = '%s %s'%(where_str, ' AND vehicle.driver_id = %s'%form['driver_id'][0])

        if form['date']:
            where_str = '%s %s'%(where_str, ''' AND s.date_order::date = '%s' '''%form['date'])

        if form['market_id']:
            where_str = '%s %s'%(where_str, ''' AND categ.id = %s '''%form['market_id'][0])

        select_str = """
              SELECT
                        coalesce(sum(l.product_uos_qty),0) as qty_unit,
                        coalesce(sum(l.product_uom_qty / u.factor * u2.factor),0) as qty_kg
                FROM (
                    sale_order_line l
                          join sale_order s on (l.order_id=s.id)
                          join res_partner part on (s.partner_id=part.id)
                          join fleet_vehicle vehicle on (s.vehicle_id=vehicle.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id)
                            left join product_product p on (l.product_id=p.id)
                                left join product_template t on (p.product_tmpl_id=t.id)
                        left join product_uom u on (u.id=l.product_uom)
                        left join product_uom u2 on (u2.id=t.uom_id))
                %s
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res

    def get_total_detail(self, form):
        where_str = ''' WHERE s.state = 'draft' AND l.product_uos is not null '''

        if form['driver_id']:
            where_str = '%s %s'%(where_str, ' AND vehicle.driver_id = %s'%form['driver_id'][0])

        if form['date']:
            where_str = '%s %s'%(where_str, ''' AND s.date_order::date = '%s' '''%form['date'])

        if form['market_id']:
            where_str = '%s %s'%(where_str, ''' AND categ.id = %s '''%form['market_id'][0])

        select_str = """
             SELECT ROW_NUMBER() OVER(ORDER BY id) AS no, * FROM (
                 SELECT
                        min(part.id) as id,
                        coalesce(sum(l.product_uos_qty),0) as qty_unit,
                        coalesce(sum(l.product_uom_qty / u.factor * u2.factor),0) as qty_kg,
                        part.name as partner
                FROM (
                    sale_order_line l
                          join sale_order s on (l.order_id=s.id)
                          join res_partner part on (s.partner_id=part.id)
                          join fleet_vehicle vehicle on (s.vehicle_id=vehicle.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id)
                            left join product_product p on (l.product_id=p.id)
                                left join product_template t on (p.product_tmpl_id=t.id)
                        left join product_uom u on (u.id=l.product_uom)
                        left join product_uom u2 on (u2.id=t.uom_id))
                %s
                GROUP BY
                        part.name,
                        part.id
                order by part.name) as foo
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res
        


    


