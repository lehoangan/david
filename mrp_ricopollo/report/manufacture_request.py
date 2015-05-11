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
            'product': self.product, 
            'get_farm': self.get_farm,
            'get_detail': self.get_detail,
            'get_product': self.get_product,
            'get_total' : self.get_total,
            'get_farm_desc': self.get_farm_desc,
        })

    def product(self, prod_id):
        res = self.pool.get('product.product').name_get(self.cr, self.uid, [prod_id])
        return res and res[0] and res[0][1] or self.pool.get('product.product').browse(self.cr, self.uid, prod_id).name

    def get_farm(self, form):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE req.state = 'draft' '''
        else:
            where_str = ''' WHERE req.state not in ('draft', 'cancel') '''

        if form['date']:
            where_str = '%s %s'%(where_str, ''' AND req.date::date = '%s' '''%form['date'])

        select_str = """
                 SELECT
                        ROW_NUMBER() OVER(ORDER BY min(req.id)) AS no,
                        w.name,
                        w.code,
                        w.id,
                        sum(req.qty_chicken) as chicken,
                        sum(req.qty_qq) as qty
                FROM 
                    (select *, (select SUM(qty_qq) FROM mrp_request_form_line where request_id = mrp_request_form.id) as qty_qq
                    FROM mrp_request_form) req 
                    join stock_warehouse w on (req.warehouse_id = w.id)
                    
                %s
                GROUP BY w.id,w.name,w.code
                order by w.name
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res

    def get_farm_desc(self, form, farm):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE req.state = 'draft' '''
        else:
            where_str = ''' WHERE req.state not in ('draft', 'cancel') '''

        if form['date']:
            where_str = '%s %s'%(where_str, ''' AND req.date::date = '%s' '''%form['date'])

        if farm and farm['id']:
            where_str = '%s %s'%(where_str, ''' AND req.warehouse_id = %s '''%farm['id'])

        select_str = """
                 SELECT
                        distinct req.description as desc
                FROM
                    mrp_request_form req
                    join stock_warehouse w on (req.warehouse_id = w.id)

                %s
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        desc = ''
        for tmp in res:
            if not desc:
                desc = tmp['desc']
            else:
                desc = '%s, %s'%(desc, tmp['desc'])
        return desc

    def get_detail(self, form, farm):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE req.state = 'draft' '''
        else:
            where_str = ''' WHERE req.state not in ('draft', 'cancel') '''

        if form['date']:
            where_str = '%s %s'%(where_str, ''' AND req.date::date = '%s' '''%form['date'])

        if farm and farm['id']:
            where_str = '%s %s'%(where_str, ''' AND req.warehouse_id = %s '''%farm['id'])
           

        select_str = """
                 SELECT
                        reql.product_id as prod,
                        sum(reql.qty_qq) as qty
                FROM 
                    mrp_request_form_line reql
                    join mrp_request_form req on (reql.request_id = req.id)
                    
                %s
                GROUP BY reql.product_id
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        for d in res:
            d['prod'] = self.product(d['prod'])
        return res

    def get_total(self, form):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE req.state = 'draft' '''
        else:
            where_str = ''' WHERE req.state not in ('draft', 'cancel') '''

        if form['date']:
            where_str = '%s %s'%(where_str, ''' AND req.date::date = '%s' '''%form['date'])

        select_str = """
                 SELECT                       
                        sum(req.qty_chicken) as chicken,
                        sum(req.qty_qq) as qty
                FROM 
                    (select *, (select SUM(qty_qq) FROM mrp_request_form_line where request_id = mrp_request_form.id) as qty_qq
                    FROM mrp_request_form) req 
                    join stock_warehouse w on (req.warehouse_id = w.id)
                    
                %s
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res
    
    def get_product(self, form):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE req.state = 'draft' '''
        else:
            where_str = ''' WHERE req.state not in ('draft', 'cancel') '''

        if form['date']:
            where_str = '%s %s'%(where_str, ''' AND req.date::date = '%s' '''%form['date'])

        select_str = """
                 SELECT
                        reql.product_id as prod,
                        sum(reql.qty_qq) as qty
                FROM 
                    mrp_request_form_line reql
                    join mrp_request_form req on (reql.request_id = req.id)
                    
                %s
                GROUP BY reql.product_id
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        for d in res:
            d['prod'] = self.product(d['prod'])
        return res


    


