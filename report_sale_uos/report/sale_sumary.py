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
            'get_market': self.get_market,
            'product': self.product,
            'get_market_payable': self.get_market_payable,
            'get_total': self.get_total,
        })

    def get_market(self, form):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE s.state = 'draft' '''
        else:
            where_str = ''' WHERE s.state not in ('draft', 'cancel')'''

        join_sql = ''
        if form['invoice_state']:
            join_sql = '''
                        INNER JOIN sale_order_line_invoice_rel inv_rel on (inv_rel.order_line_id = l.id)
                        INNER JOIN account_invoice_line inv_l on (inv_l.id = inv_rel.invoice_id)
                        INNER JOIN account_invoice inv on (inv.id = inv_l.invoice_id)
            '''
            if form['invoice_state'] == 'draft':
                where_str = '%s %s'%(where_str, ''' AND inv.state = 'draft' ''')
            elif form['invoice_state'] == 'done':
                where_str = '%s %s'%(where_str, ''' AND inv.state not in ('draft', 'cancel') ''')
            else:
                where_str = '%s %s'%(where_str, ''' AND inv.state != 'cancel' ''')

        if form['datetime_from']:
            where_str = '%s %s'%(where_str, ''' AND s.date_order >= '%s' '''%form['datetime_from'])

        if form['datetime_to']:
            where_str = '%s %s'%(where_str, ''' AND s.date_order <= '%s' '''%form['datetime_to'])

        if form['product_ids']:
            prod_ids = form['product_ids']
            if prod_ids:
                prod_ids += [-1,-1]
            where_str = '%s %s'%(where_str, ''' AND l.product_id in %s '''%str(tuple(prod_ids)))
        select_str = """
                 SELECT
                        distinct (categ.id) as id,
                        categ.name,
                        part.city,
                        sum(l.product_uom_qty* l.price_unit) as amount,
                        sum(l.discount_kg * l.price_unit * (100.0-l.discount) / 100.0 + l.product_uom_qty * l.price_unit * l.discount / 100.0) as discount
                FROM (
                    sale_order_line l
                          join sale_order s on (l.order_id=s.id)
                          join res_partner part on (s.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                %s
                GROUP BY categ.name,categ.id, part.city
                order by categ.name
        """%(join_sql, where_str)

        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        for categ in res:
            if not categ['id']: continue
            result = self.pool.get('res.partner.category').name_get(self.cr, self.uid, categ['id'])
            if result and result[0]:
                categ['name'] = result[0][1]
        return res

    def get_market_payable(self, form, state_id):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE s.state = 'draft' '''
        else:
            where_str = ''' WHERE s.state not in ('draft', 'cancel')'''

        join_sql = ''
        if form['invoice_state']:
            join_sql = '''
                        INNER JOIN sale_order_line_invoice_rel inv_rel on (inv_rel.order_line_id = l.id)
                        INNER JOIN account_invoice_line inv_l on (inv_l.id = inv_rel.invoice_id)
                        INNER JOIN account_invoice inv on (inv.id = inv_l.invoice_id)
            '''
            if form['invoice_state'] == 'draft':
                where_str = '%s %s'%(where_str, ''' AND inv.state = 'draft' ''')
            elif form['invoice_state'] == 'done':
                where_str = '%s %s'%(where_str, ''' AND inv.state not in ('draft', 'cancel') ''')
            else:
                where_str = '%s %s'%(where_str, ''' AND inv.state != 'cancel' ''')

        context = {}
        if form['datetime_from']:
            where_str = '%s %s'%(where_str, ''' AND s.date_order >= '%s' '''%form['datetime_from'])
            context.update({'date_to':form['datetime_from']})

        if form['datetime_to']:
            where_str = '%s %s'%(where_str, ''' AND s.date_order <= '%s' '''%form['datetime_to'])
            # context.update({'date_to':form['datetime_to']})

        if state_id:
            if state_id['id']:
                where_str = '%s %s'%(where_str, ''' AND categ.id = %s '''%state_id['id'])
            else:
                where_str = '%s %s'%(where_str, ''' AND categ.id is null''')

        select_str = """
                 SELECT
                        distinct (s.partner_id) as partner_id

                FROM
                    sale_order_line l
                          join sale_order s on (l.order_id=s.id)
                          join res_partner part on (s.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id)
                %s
                %s
        """%(join_sql, where_str)

        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        total = 0
        partner_obj = self.pool.get('res.partner')
        for part in res:
            total += partner_obj.browse(self.cr, self.uid, part['partner_id'], context).debit
        return total

    def get_detail(self, form, state_id):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE s.state = 'draft' '''
        else:
            where_str = ''' WHERE s.state not in ('draft', 'cancel')'''

        join_sql = ''
        if form['invoice_state']:
            join_sql = '''
                        INNER JOIN sale_order_line_invoice_rel inv_rel on (inv_rel.order_line_id = l.id)
                        INNER JOIN account_invoice_line inv_l on (inv_l.id = inv_rel.invoice_id)
                        INNER JOIN account_invoice inv on (inv.id = inv_l.invoice_id)
            '''
            if form['invoice_state'] == 'draft':
                where_str = '%s %s'%(where_str, ''' AND inv.state = 'draft' ''')
            elif form['invoice_state'] == 'done':
                where_str = '%s %s'%(where_str, ''' AND inv.state not in ('draft', 'cancel') ''')
            else:
                where_str = '%s %s'%(where_str, ''' AND inv.state != 'cancel' ''')

        if form['datetime_from']:
            where_str = '%s %s'%(where_str, ''' AND s.date_order >= '%s' '''%form['datetime_from'])

        if form['datetime_to']:
            where_str = '%s %s'%(where_str, ''' AND s.date_order <= '%s' '''%form['datetime_to'])

        if state_id:
            if state_id['id']:
                where_str = '%s %s'%(where_str, ''' AND categ.id = %s '''%state_id['id'])
            else:
                where_str = '%s %s'%(where_str, ''' AND categ.id is null''')

        if form['product_ids']:
            prod_ids = form['product_ids']
            if prod_ids:
                prod_ids += [-1,-1]
            where_str = '%s %s'%(where_str, ''' AND l.product_id in %s '''%str(tuple(prod_ids)))
        select_str = """
             SELECT ROW_NUMBER() OVER(ORDER BY id) AS no, * FROM (
                 SELECT
                        min(l.id) as id,
                        p.id as prod_id,
                        t.uos_id as product_uos,
                        --sum(l.product_uos_qty / us.factor * us2.factor) as uos,
                        sum(l.product_uos_qty) as uos,
                        t.uom_id as product_uom,
                        sum(l.product_uom_qty / u.factor * u2.factor) as uom,
                        sum(l.product_uom_qty * l.price_unit) as amount,
                        sum(l.product_uom_qty * l.price_unit * l.discount / 100.0) as disc_percent_amount,
                        sum(l.discount_kg * l.price_unit * (100.0-l.discount) / 100.0 + l.product_uom_qty * l.price_unit * l.discount / 100.0) as disc_amount,
                        sum(l.discount_kg / u.factor * u2.factor) as disc_kg,
                        sum(l.discount_kg * l.price_unit * (100.0-l.discount) / 100.0) as disc_kg_amount

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
                %s
                GROUP BY l.product_id,
                        t.uom_id,
                        t.name,
                        p.id,
                        t.uos_id
                order by t.name) as foo
        """%(join_sql, where_str)
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res
    
    def product(self, prod_id):
        res = self.pool.get('product.product').name_get(self.cr, self.uid, [prod_id])
        return res and res[0] and res[0][1] or self.pool.get('product.product').browse(self.cr, self.uid, prod_id).name

    def get_total(self, form):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE s.state = 'draft' '''
        else:
            where_str = ''' WHERE s.state not in ('draft', 'cancel')'''

        join_sql = ''
        if form['invoice_state']:
            join_sql = '''
                        INNER JOIN sale_order_line_invoice_rel inv_rel on (inv_rel.order_line_id = l.id)
                        INNER JOIN account_invoice_line inv_l on (inv_l.id = inv_rel.invoice_id)
                        INNER JOIN account_invoice inv on (inv.id = inv_l.invoice_id)
            '''
            if form['invoice_state'] == 'draft':
                where_str = '%s %s'%(where_str, ''' AND inv.state = 'draft' ''')
            elif form['invoice_state'] == 'done':
                where_str = '%s %s'%(where_str, ''' AND inv.state not in ('draft', 'cancel') ''')
            else:
                where_str = '%s %s'%(where_str, ''' AND inv.state != 'cancel' ''')
        context = {}
        if form['datetime_from']:
            where_str = '%s %s'%(where_str, ''' AND s.date_order >= '%s' '''%form['datetime_from'])
            context.update({'date_to':form['datetime_from']})

        if form['datetime_to']:
            where_str = '%s %s'%(where_str, ''' AND s.date_order <= '%s' '''%form['datetime_to'])
            #context.update({'date_to':form['datetime_to']})

        if form['product_ids']:
            prod_ids = form['product_ids']
            if prod_ids:
                prod_ids += [-1,-1]
            where_str = '%s %s'%(where_str, ''' AND l.product_id in %s '''%str(tuple(prod_ids)))
        select_str = """
                 SELECT
                        sum(l.product_uom_qty * l.price_unit) as amount,
                        sum(l.discount_kg * l.price_unit * (100.0-l.discount) / 100.0 + l.product_uom_qty * l.price_unit * l.discount / 100.0) as discount
                FROM (
                    sale_order_line l
                          join sale_order s on (l.order_id=s.id)
                          join res_partner part on (s.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                %s
        """%(join_sql, where_str)

        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        select_str = """
                 SELECT
                        distinct (s.partner_id) as partner_id

                FROM
                    sale_order_line l
                          join sale_order s on (l.order_id=s.id)
                          join res_partner part on (s.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id)
                %s
                %s
        """%(join_sql, where_str)

        self.cr.execute(select_str)
        res1 = self.cr.dictfetchall()

        if res and res[0]:
            total = 0
            partner_obj = self.pool.get('res.partner')
            for part in res1:
                total += partner_obj.browse(self.cr, self.uid, part['partner_id'], context).debit

            if res[0] and res[0]['amount']:
                total += res[0]['amount']
            res[0].update({'payable': total})

        return res
        
    


