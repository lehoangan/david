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
            'get_market': self.get_market,
            'get_total_market': self.get_total_market,
            'get_cost_of_market': self.get_cost_of_market,
            'get_product': self.get_product,
            'get_market_product': self.get_market_product,
            'get_disc_percent': self.get_disc_percent,
            'get_disc_kg': self.get_disc_kg,
            'get_expence_market': self.get_expence_market,
            'get_cost_total': self.get_cost_total,
            'get_market_product_total': self.get_market_product_total,
            'get_disc_percent_total': self.get_disc_percent_total,
            'get_disc_kg_total': self.get_disc_kg_total,
            'get_expence_market_total': self.get_expence_market_total,
            'get_cost_of_market2': self.get_cost_of_market2,
            'get_cost_of_market2_total': self.get_cost_of_market2_total,
            'get_cost_of_market2_total_percent': self.get_cost_of_market2_total_percent,
        })

    def get_market(self, form):
        where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])

        if form['product_ids']:
            prod_ids = form['product_ids']
            if prod_ids:
                prod_ids += [-1,-1]
            where_str = '%s %s'%(where_str, ''' AND l.product_id in %s '''%str(tuple(prod_ids)))
        select_str = """
                 SELECT
                        distinct (categ.id) as id,
                        categ.name,
                        sum(l.price_subtotal) as amount
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
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

    def get_total_market(self, form):
        where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])

        if form['product_ids']:
            prod_ids = form['product_ids']
            if prod_ids:
                prod_ids += [-1,-1]
            where_str = '%s %s'%(where_str, ''' AND l.product_id in %s '''%str(tuple(prod_ids)))
        select_str = """
                 SELECT
                        coalesce(sum(l.price_subtotal),0) as amount
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchone()
        return res

    def get_cost_of_market(self, form):
        where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])


        if form['product_ids']:
            prod_ids = form['product_ids']
            if prod_ids:
                prod_ids += [-1,-1]
            where_str = '%s %s'%(where_str, ''' AND l.product_id in %s '''%str(tuple(prod_ids)))

        select_str = """
                 SELECT
                        distinct (categ.id) as id,
                        categ.name,
                        coalesce(sum(l.price_subtotal),0) as amount
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                GROUP BY categ.name,categ.id
                order by categ.name
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        results = {}
        for categ in res:
            if not categ['id']:
                categ['id'] = -1
                categ['name'] = 'zzzzzzzzz'
            if categ['id'] not in results.keys():
                results.update({
                    categ['id']: {'total': 0,
                                 'amount': 0,
                                 'name': categ['name']}
                })

            results[categ['id']]['amount'] +=  categ['amount']
            results[categ['id']]['total'] +=  categ['amount']

        select_str = """
                 SELECT
                        distinct (categ.id) as id,
                        sum(l.quantity) as quantity,
                        categ.name,
                        l.product_id
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                GROUP BY l.product_id,categ.id,categ.name
                order by categ.name
                """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        product_obj = self.pool.get('product.product')

        for data in res:
            if not data['id']: data['id'] = -1

            cost = product_obj.browse(self.cr, self.uid, data['product_id']).standard_price
            results[data['id']]['total'] -= cost * data['quantity']
        return_data = sorted(results.values(), key=lambda k: k['name'])
        return return_data

    def get_product(self, form):
        where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])

        if form['product_ids']:
            prod_ids = form['product_ids']
            if prod_ids:
                prod_ids += [-1,-1]
            where_str = '%s %s'%(where_str, ''' AND l.product_id in %s '''%str(tuple(prod_ids)))
        select_str = """
                 SELECT
                        distinct l.product_id as id
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        for data in res:
            prod = self.pool.get('product.product').name_get(self.cr, self.uid, [data['id']])
            name = prod and prod[0] and prod[0][1] or self.pool.get('product.product').browse(self.cr, self.uid, data['id']).name
            data.update({'name': name})
        return sorted(res, key=lambda k: k['name'])

    def get_market_product(self, form, product):
        where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])

        if form['product_ids']:
            prod_ids = form['product_ids']
            if prod_ids:
                prod_ids += [-1,-1]
            where_str = '%s %s'%(where_str, ''' AND l.product_id in %s '''%str(tuple(prod_ids)))

        select_str1 = """
                 SELECT CASE
                          WHEN id is not null THEN id
                          ELSE -1
                        END as id,
                        name, amount_prod
                FROM (SELECT
                        distinct (categ.id) as id,
                        categ.name,
                        coalesce(sum(l.price_subtotal),0) as amount_prod
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s AND l.product_id = %s
                GROUP BY categ.name,categ.id
                order by categ.name) as temp1
        """%(where_str,product['id'])

        select_str2 = """
                 SELECT CASE
                          WHEN id is not null THEN id
                          ELSE -1
                        END as id,
                        name, amount
                FROM (SELECT
                        distinct (categ.id) as id,
                        categ.name,
                        coalesce(sum(l.price_subtotal),0) as amount
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                GROUP BY categ.name,categ.id
                order by categ.name) as temp2
        """%(where_str)
        select_str = ''' select sql2.id, sql2.name, sql1.amount_prod, sql2.amount, round((sql1.amount_prod/sql2.amount)*100, 2) as percent
                            FROM (%s) as sql2
                            LEFT JOIN (%s) as sql1 on (sql1.id=sql2.id)
                            order by sql2.name'''%(select_str2, select_str1)
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res

    def get_disc_kg(self, form):
        where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])

        if form['product_ids']:
            prod_ids = form['product_ids']
            if prod_ids:
                prod_ids += [-1,-1]
            where_str = '%s %s'%(where_str, ''' AND l.product_id in %s '''%str(tuple(prod_ids)))

        select_str1 = """
                 SELECT CASE
                          WHEN id is not null THEN id
                          ELSE -1
                        END as id,
                        name, amount_disc
                FROM (SELECT
                        distinct (categ.id) as id,
                        categ.name,
                        coalesce(sum(l.discount_kg * l.price_unit * (100.0-l.discount)) / 100.0,0) as amount_disc
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                GROUP BY categ.name,categ.id
                order by categ.name) as temp1
        """%(where_str)

        select_str2 = """
                 SELECT CASE
                          WHEN id is not null THEN id
                          ELSE -1
                        END as id,
                        name, amount
                FROM (SELECT
                        distinct (categ.id) as id,
                        categ.name,
                        coalesce(sum(l.price_subtotal),0) as amount
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                GROUP BY categ.name,categ.id
                order by categ.name) as temp2
        """%(where_str)
        select_str = ''' select sql2.id, sql2.name, sql1.amount_disc, sql2.amount, round((sql1.amount_disc/sql2.amount)*100, 2) as percent
                            FROM (%s) as sql2
                            LEFT JOIN (%s) as sql1 on (sql1.id=sql2.id)
                            order by sql2.name'''%(select_str2, select_str1)
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res

    def get_disc_percent(self, form):
        where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])

        if form['product_ids']:
            prod_ids = form['product_ids']
            if prod_ids:
                prod_ids += [-1,-1]
            where_str = '%s %s'%(where_str, ''' AND l.product_id in %s '''%str(tuple(prod_ids)))

        select_str1 = """
                 SELECT CASE
                          WHEN id is not null THEN id
                          ELSE -1
                        END as id,
                        name, amount_disc
                FROM (SELECT
                        distinct (categ.id) as id,
                        categ.name,
                        coalesce(sum(l.product_uom_qty * l.price_unit * l.discount / 100.0),0) as amount_disc
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                GROUP BY categ.name,categ.id
                order by categ.name) as temp1
        """%(where_str)

        select_str2 = """
                 SELECT CASE
                          WHEN id is not null THEN id
                          ELSE -1
                        END as id,
                        name, amount
                FROM (SELECT
                        distinct (categ.id) as id,
                        categ.name,
                        coalesce(sum(l.price_subtotal),0) as amount
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                GROUP BY categ.name,categ.id
                order by categ.name) as temp2
        """%(where_str)
        select_str = ''' select sql2.id, sql2.name, sql1.amount_disc, sql2.amount, round((sql1.amount_disc/sql2.amount)*100, 2) as percent
                            FROM (%s) as sql2
                            LEFT JOIN (%s) as sql1 on (sql1.id=sql2.id)
                            order by sql2.name'''%(select_str2, select_str1)
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res

    def get_expence_market(self, form):
        where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])

        if form['product_ids']:
            prod_ids = form['product_ids']
            if prod_ids:
                prod_ids += [-1,-1]
            where_str = '%s %s'%(where_str, ''' AND l.product_id in %s '''%str(tuple(prod_ids)))
        select_str = """
                 SELECT
                        distinct (categ.id) as id,
                        categ.name,
                        0 as amount,
                        0 as percent,
                        coalesce(sum(l.price_subtotal),0) as total
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                GROUP BY categ.name,categ.id
                order by categ.name
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        config_obj = self.pool.get('config.report.rico')
        config_ids = config_obj.search(self.cr, self.uid, [])
        if config_ids:
            config_brw = config_obj.browse(self.cr, self.uid, config_ids[0], {'date_from': form['date_from'],
                                                                              'date_to': form['date_to'],})
            all_total = sum(acc.balance for acc in config_brw.account_ids)/2
            each = res and all_total / len(res) or 0
            speical = config_brw.account_id.balance
            local = {}
            all_total = sum(acc.balance for acc in config_brw.local_account_ids)
            each_local = config_brw.categ_ids and all_total / len(config_brw.categ_ids) or 0
            for categ in config_brw.categ_ids:
                local.update({categ.id: each_local})
            for categ in res:
                categ['amount'] += each
                if config_brw.categ_id and categ['id'] == config_brw.categ_id.id:
                    categ['amount'] += speical
                if categ['id'] in local.keys():
                    categ['amount'] += local[categ['id']]
                categ['percent'] = round(categ['amount']/categ['total']*100, 2)
        return res

    def get_cost_total(self, form):
        where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])


        if form['product_ids']:
            prod_ids = form['product_ids']
            if prod_ids:
                prod_ids += [-1,-1]
            where_str = '%s %s'%(where_str, ''' AND l.product_id in %s '''%str(tuple(prod_ids)))

        select_str = """
                 SELECT
                        coalesce(sum(l.price_subtotal),0) as amount
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
        """%where_str
        self.cr.execute(select_str)
        result = self.cr.dictfetchone()

        select_str = """
                 SELECT
                        sum(l.quantity) as quantity,
                        l.product_id
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                GROUP BY l.product_id
                """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        product_obj = self.pool.get('product.product')

        for data in res:
            cost = product_obj.browse(self.cr, self.uid, data['product_id']).standard_price
            result['amount'] -= cost * data['quantity']
        return result

    def get_market_product_total(self, form, product):
        where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])

        if form['product_ids']:
            prod_ids = form['product_ids']
            if prod_ids:
                prod_ids += [-1,-1]
            where_str = '%s %s'%(where_str, ''' AND l.product_id in %s '''%str(tuple(prod_ids)))

        select_str = """
                 SELECT
                        coalesce(sum(l.price_subtotal),0) as amount
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s AND l.product_id = %s
        """%(where_str,product['id'])

        self.cr.execute(select_str)
        res = self.cr.dictfetchone()
        return res

    def get_disc_kg_total(self, form):
        where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])

        if form['product_ids']:
            prod_ids = form['product_ids']
            if prod_ids:
                prod_ids += [-1,-1]
            where_str = '%s %s'%(where_str, ''' AND l.product_id in %s '''%str(tuple(prod_ids)))

        select_str = """
                 SELECT
                        coalesce(sum(l.discount_kg * l.price_unit * (100.0-l.discount)) / 100.0,0) as amount
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
        """%(where_str)

        self.cr.execute(select_str)
        res = self.cr.dictfetchone()
        return res

    def get_disc_percent_total(self, form):
        where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])

        if form['product_ids']:
            prod_ids = form['product_ids']
            if prod_ids:
                prod_ids += [-1,-1]
            where_str = '%s %s'%(where_str, ''' AND l.product_id in %s '''%str(tuple(prod_ids)))

        select_str = """
                 SELECT
                        coalesce(sum(l.product_uom_qty * l.price_unit * l.discount / 100.0),0) as amount
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
        """%(where_str)

        self.cr.execute(select_str)
        res = self.cr.dictfetchone()
        return res

    def get_expence_market_total(self, form):
        where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])

        if form['product_ids']:
            prod_ids = form['product_ids']
            if prod_ids:
                prod_ids += [-1,-1]
            where_str = '%s %s'%(where_str, ''' AND l.product_id in %s '''%str(tuple(prod_ids)))
        select_str = """
                 SELECT
                        distinct (categ.id) as id,
                        categ.name,
                        0 as amount,
                        0 as percent,
                        coalesce(sum(l.price_subtotal),0) as total
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                GROUP BY categ.name,categ.id
                order by categ.name
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        config_obj = self.pool.get('config.report.rico')
        config_ids = config_obj.search(self.cr, self.uid, [])
        total1, total2 = 0,0
        if config_ids:
            config_brw = config_obj.browse(self.cr, self.uid, config_ids[0], {'date_from': form['date_from'],
                                                                              'date_to': form['date_to'],})
            total1 += sum(acc.balance for acc in config_brw.account_ids)/2
            total1 += config_brw.account_id.balance
            total1 += sum(acc.balance for acc in config_brw.local_account_ids)
            for categ in res:
                total2 += categ['total']
        return total1, total2 and round(total1/total2 *100,2) or 0

    def get_cost_of_market2(self, form):
        where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])


        if form['product_ids']:
            prod_ids = form['product_ids']
            if prod_ids:
                prod_ids += [-1,-1]
            where_str = '%s %s'%(where_str, ''' AND l.product_id in %s '''%str(tuple(prod_ids)))

        select_str = """
                 SELECT
                        distinct (categ.id) as id,
                        categ.name,
                        coalesce(sum(l.price_subtotal),0) as amount
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                GROUP BY categ.name,categ.id
                order by categ.name
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        results = {}
        for categ in res:
            if not categ['id']:
                categ['id'] = -1
                categ['name'] = 'zzzzzzzzz'
            if categ['id'] not in results.keys():
                results.update({
                    categ['id']: {'total': 0,
                                 'amount': 0,
                                 'name': categ['name']}
                })

            results[categ['id']]['amount'] +=  categ['amount']
            results[categ['id']]['total'] +=  categ['amount']

        select_str = """
                 SELECT
                        distinct (categ.id) as id,
                        sum(l.quantity) as quantity,
                        categ.name,
                        l.product_id
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                GROUP BY l.product_id,categ.id,categ.name
                order by categ.name
                """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        product_obj = self.pool.get('product.product')

        for data in res:
            if not data['id']: data['id'] = -1

            cost = product_obj.browse(self.cr, self.uid, data['product_id']).standard_price
            results[data['id']]['total'] -= cost * data['quantity']

        select_str = """
                SELECT
                        distinct (categ.id) as id,
                        categ.name,
                        coalesce(sum(l.product_uom_qty * l.price_unit * l.discount / 100.0),0) as amount_disc
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                GROUP BY categ.name,categ.id
                order by categ.name
        """%(where_str)
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()

        for data in res:
            if not data['id']: data['id'] = -1
            results[data['id']]['total'] -= data['amount_disc'] and data['amount_disc'] or 0

        res = self.get_expence_market(form)
        for data in res:
            if not data['id']: data['id'] = -1
            results[data['id']]['total'] -= data['amount']

        select_str = """
                SELECT
                        distinct (categ.id) as id,
                        categ.name,
                        coalesce(sum(l.discount_kg * l.price_unit * (100.0-l.discount)) / 100.0,0) as amount_disc
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                GROUP BY categ.name,categ.id
                order by categ.name
        """%(where_str)
        self.cr.execute(select_str)
        res_kg = self.cr.dictfetchall()

        for data in res_kg:
            if not data['id']: data['id'] = -1
            results[data['id']]['total'] -= data['amount_disc'] and data['amount_disc'] or 0
            results[data['id']]['amount'] = data['amount_disc'] and data['amount_disc'] or 0

        return_data = sorted(results.values(), key=lambda k: k['name'])
        return return_data

    def get_cost_of_market2_total(self, form):
        where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])


        if form['product_ids']:
            prod_ids = form['product_ids']
            if prod_ids:
                prod_ids += [-1,-1]
            where_str = '%s %s'%(where_str, ''' AND l.product_id in %s '''%str(tuple(prod_ids)))

        select_str = """
                 SELECT
                        coalesce(sum(l.price_subtotal),0) as amount
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
        """%where_str
        self.cr.execute(select_str)
        total = self.cr.dictfetchone()['amount']
        select_str = """
                 SELECT
                        sum(l.quantity) as quantity,
                        l.product_id
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                GROUP BY l.product_id
                """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        product_obj = self.pool.get('product.product')
        for data in res:
            cost = product_obj.browse(self.cr, self.uid, data['product_id']).standard_price
            total -= cost * data['quantity']

        select_str = """
                SELECT
                        coalesce(sum(l.product_uom_qty * l.price_unit * l.discount / 100.0),0) as amount_disc
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
        """%(where_str)
        self.cr.execute(select_str)
        total -= self.cr.dictfetchone()['amount_disc']

        res = self.get_expence_market(form)
        for data in res:
           total -= data['amount']

        select_str = """
                SELECT
                        coalesce(sum(l.discount_kg * l.price_unit * (100.0-l.discount)) / 100.0,0) as amount_disc
                FROM ( account_invoice inv
                          join account_invoice_line l on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
        """%(where_str)
        self.cr.execute(select_str)
        total -= self.cr.dictfetchone()['amount_disc']
        return total

    def get_cost_of_market2_total_percent(self, form):
        total = self.get_cost_of_market2_total(form)
        total_kg = self.get_disc_kg_total(form)
        percent = 0
        if total_kg and total_kg['amount']:
            percent = round(total/total_kg['amount']*100, 2)
        return percent


