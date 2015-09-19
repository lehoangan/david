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
            'get_warehouse': self.get_warehouse,
        })

    def location(self, lot_id):
        res = self.pool.get('stock.location').name_get(self.cr, self.uid, [lot_id])
        return res and res[0] and res[0][1] or self.pool.get('stock.location').browse(self.cr, self.uid, lot_id).name
    
    def get_warehouse(self, form):

        select_str = """
                 SELECT ROW_NUMBER() OVER(ORDER BY warehouse.id) AS no, warehouse.code,
                    warehouse.name, warehouse.lot_stock_id as lot_name,
                    warehouse.is_farm, acc.name as acc_name, acc.code as acc_code, warehouse.capacity,
                    partner.name as responsable FROM stock_warehouse warehouse
                    LEFT JOIN res_users u on (u.id=warehouse.manager_id)
                    JOIN res_partner partner on (u.partner_id=partner.id)
                    LEFT JOIN account_account acc on (warehouse.account_id = acc.id)
        """
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        for d in res:
            d['lot_name'] = self.location(d['lot_name'])
        return res


    


