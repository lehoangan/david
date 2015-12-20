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
            'get_state': self.get_state,
            'get_location': self.get_location,
        })

    def get_state(self):
        return {'draft': 'Nuevo','done': 'Realizado',
                'waiting': 'Esperando otro movimiento',
                'cancel': 'Cancelado', 'assigned': 'Listo para Hacer',
                'confirmed': 'Esperando disponibilidad'}

    def get_location(self, location_id):
        warehouse = self.pool.get('stock.warehouse')
        warehouse_ids = warehouse.search(self.cr, self.uid, [('lot_stock_id', '=', location_id)])
        if warehouse_ids:
            return warehouse.name_get(self.cr, self.uid, warehouse_ids[0])[0][1]
        else:
            return self.pool.get('stock.location').browse(self.cr, self.uid, location_id).name

    def get_detail(self, form):
        warehouse = self.pool.get('stock.warehouse').browse(self.cr, self.uid, form['warehouse_id'][0])
        location_id = warehouse.lot_stock_id.id
        where_str = 'WHERE (move.location_id = %s OR move.location_dest_id = %s) '%(location_id, location_id)
        if form['state']:
            where_str += ''' AND move.state = '%s' '''%form['state']

        if form['datetime_from']:
            where_str = '%s %s'%(where_str, ''' AND move.date >= '%s' '''%form['datetime_from'])

        if form['datetime_to']:
            where_str = '%s %s'%(where_str, ''' AND move.date <= '%s' '''%form['datetime_to'])
        select_str = """
                 SELECT ROW_NUMBER() OVER(ORDER BY move.id) AS no,
                    pick.name, move.date, pick.min_date, move.name as desc, pick.origin as source,
                    tmpl.name as prod, move.product_uom_qty as qty, uom.name as uom, move.price_unit,
                    (move.price_unit * move.product_uom_qty) as amount, move.location_id as location,
                    move.location_dest_id as dest_location, move.state

                FROM stock_move move
                LEFT JOIN stock_picking pick on (move.picking_id = pick.id)
                JOIN product_product prod on (move.product_id = prod.id)
                JOIN product_template tmpl on (prod.product_tmpl_id = tmpl.id)
                JOIN product_uom uom on (move.product_uom = uom.id)
                %s
                order by move.date, pick.name
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res

