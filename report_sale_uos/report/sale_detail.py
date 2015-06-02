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
            'get_user': self.get_user,
            'get_detail': self.get_detail,
            'product': self.product,
            'get_market': self.get_market,
            'get_total_detail': self.get_total_detail,
            'get_total': self.get_total,
        })

    def get_market(self, form):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE so.state = 'draft' '''
        else:
            where_str = ''' WHERE so.state not in ('draft', 'cancel')'''

        if form['user_id']:
            where_str = '%s %s'%(where_str, ' AND so.user_id = %s'%form['user_id'][0])

        if form['partner_id']:
            where_str = '%s %s'%(where_str, ' AND so.partner_id = %s'%form['partner_id'][0])

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND so.date_order::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND so.date_order::date <= '%s' '''%form['date_to'])
        select_str = """
                 SELECT
                        distinct (categ.id) as id,
                        categ.name
                FROM ( sale_order so
                          join res_partner part on (so.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                GROUP BY categ.name,categ.id
                order by categ.name
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        
        for categ in res:
            if not categ['id']: continue
            result = self.pool.get('res.partner.category').name_get(self.cr, self.uid, categ['id'])
            if result and result[0]:
                categ['name'] = result[0][1]
        return res

    def get_user(self, form, state_id):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE so.state = 'draft' '''
        else:
            where_str = ''' WHERE so.state not in ('draft', 'cancel')'''

        if form['user_id']:
            where_str = '%s %s'%(where_str, ' AND usr.id = %s'%form['user_id'][0])

        if form['partner_id']:
            where_str = '%s %s'%(where_str, ' AND so.partner_id = %s'%form['partner_id'][0])

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND so.date_order::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND so.date_order::date <= '%s' '''%form['date_to'])

        if state_id:
            # if state_id['city']:
            #     where_str = '%s %s'%(where_str, ''' AND part.city = '%s' '''%state_id['city'])
            # else:
            #     where_str = '%s %s'%(where_str, ''' AND part.city is null ''')
            if state_id['id']:
                where_str = '%s %s'%(where_str, ''' AND categ.id = %s '''%state_id['id'])
            else:
                where_str = '%s %s'%(where_str, ''' AND categ.id is null''')

        sql = '''
                SELECT distinct so.user_id, part2.name
                      FROM sale_order so
                      INNER JOIN res_partner part on (so.partner_id=part.id)
                      INNER JOIN res_users usr on (so.user_id=usr.id)
                      INNER JOIN res_partner part2 on (usr.partner_id=part2.id)
                      left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                      left join res_partner_category categ on (rel.category_id=categ.id)

                %s
        '''%where_str
        self.cr.execute(sql)
        res = self.cr.dictfetchall()
        return res



    def get_detail(self, form, user, state_id):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE s.state = 'draft' '''
        else:
            where_str = ''' WHERE s.state not in ('draft', 'cancel')'''

        where_str = '%s %s'%(where_str, ' AND s.user_id = %s'%user['user_id'])

        if form['partner_id']:
            where_str = '%s %s'%(where_str, ' AND s.partner_id = %s'%form['partner_id'][0])

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND s.date_order::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND s.date_order::date <= '%s' '''%form['date_to'])

        if state_id:
            # if state_id['city']:
            #     where_str = '%s %s'%(where_str, ''' AND part.city = '%s' '''%state_id['city'])
            # else:
            #     where_str = '%s %s'%(where_str, ''' AND part.city is null ''')
            if state_id['id']:
                where_str = '%s %s'%(where_str, ''' AND categ.id = %s '''%state_id['id'])
            else:
                where_str = '%s %s'%(where_str, ''' AND categ.id is null''')

        select_str = """
             SELECT ROW_NUMBER() OVER(ORDER BY id) AS no, * FROM (
                 SELECT
                        min(l.id) as id,
                        t.name,
                        p.id as prod_id,
                        t.uos_id as product_uos,
                        --sum(l.product_uos_qty / us.factor * us2.factor) as product_uos_qty,
                        sum(l.product_uos_qty) as product_uos_qty,
                        t.uom_id as product_uom,
                        sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
                        sum((l.product_uom_qty-l.discount_kg) * l.price_unit * (100.0-l.discount) / 100.0) as price_total,
                        s.name as so,
                        part.name as partner,
                        s.user_id as user_id,
                        s.state,
                        s.is_ok
                FROM (
                    sale_order_line l
                          join sale_order s on (l.order_id=s.id)
                          join res_partner part on (s.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id)
                            left join product_product p on (l.product_id=p.id)
                                left join product_template t on (p.product_tmpl_id=t.id)
                        left join product_uom u on (u.id=l.product_uom)
                        left join product_uom u2 on (u2.id=t.uom_id)
                        left join product_uom us on (us.id=l.product_uos)
                        left join product_uom us2 on (us2.id=t.uom_id) )
                %s
                GROUP BY l.product_id,
                        t.uom_id,
                        t.name,
                        p.id,
                        part.name,
                        s.user_id,
                        s.state,
                        s.name,
                        t.uos_id,
                        s.is_ok
                order by part.name, t.name) as foo
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res
    
    def product(self, prod_id):
        res = self.pool.get('product.product').name_get(self.cr, self.uid, [prod_id])
        return res and res[0] and res[0][1] or self.pool.get('product.product').browse(self.cr, self.uid, prod_id).name

    def get_total_detail(self, form):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE s.state = 'draft' '''
        else:
            where_str = ''' WHERE s.state not in ('draft', 'cancel')'''

        if form['user_id']:
            where_str = '%s %s'%(where_str, ' AND s.user_id = %s'%form['user_id'][0])

        if form['partner_id']:
            where_str = '%s %s'%(where_str, ' AND s.partner_id = %s'%form['partner_id'][0])

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND s.date_order::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND s.date_order::date <= '%s' '''%form['date_to'])

        select_str = """
             SELECT ROW_NUMBER() OVER(ORDER BY id) AS no, * FROM (
                 SELECT
                        p.id as id,
                        sum(l.product_uos_qty) as product_uos_qty,
                        sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
                        sum((l.product_uom_qty-l.discount_kg) * l.price_unit * (100.0-l.discount) / 100.0) as price_total
                FROM (
                    sale_order_line l
                          join sale_order s on (l.order_id=s.id)
                          join res_partner part on (s.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id)
                            left join product_product p on (l.product_id=p.id)
                                left join product_template t on (p.product_tmpl_id=t.id)
                        left join product_uom u on (u.id=l.product_uom)
                        left join product_uom u2 on (u2.id=t.uom_id)
                        left join product_uom us on (us.id=l.product_uos)
                        left join product_uom us2 on (us2.id=t.uom_id) )
                %s
                GROUP BY
                        p.id) as foo
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res

    def get_total(self, form):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE s.state = 'draft' '''
        else:
            where_str = ''' WHERE s.state not in ('draft', 'cancel')'''

        if form['user_id']:
            where_str = '%s %s'%(where_str, ' AND s.user_id = %s'%form['user_id'][0])

        if form['partner_id']:
            where_str = '%s %s'%(where_str, ' AND s.partner_id = %s'%form['partner_id'][0])

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND s.date_order::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND s.date_order::date <= '%s' '''%form['date_to'])

        select_str = """
                 SELECT
                        sum(l.product_uos_qty) as product_uos_qty,
                        sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
                        sum((l.product_uom_qty-l.discount_kg) * l.price_unit * (100.0-l.discount) / 100.0) as price_total
                FROM (
                    sale_order_line l
                          join sale_order s on (l.order_id=s.id)
                          join res_partner part on (s.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id)
                            left join product_product p on (l.product_id=p.id)
                                left join product_template t on (p.product_tmpl_id=t.id)
                        left join product_uom u on (u.id=l.product_uom)
                        left join product_uom u2 on (u2.id=t.uom_id)
                        left join product_uom us on (us.id=l.product_uos)
                        left join product_uom us2 on (us2.id=t.uom_id) )
                %s
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res
        
    


