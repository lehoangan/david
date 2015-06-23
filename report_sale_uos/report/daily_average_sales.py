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
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import time

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'datetime': datetime,
            'get_customer': self.get_customer,
            'get_product': self.get_product,
            'get_date': self.get_date,
            'get_market': self.get_market,
        })

    def get_date(self, form):
        result = []
        for datetmp in form['lst_date']:
            date = datetime.datetime.strptime(datetmp[0], DEFAULT_SERVER_DATE_FORMAT)
            result += [[
                datetmp[0],
                (date + datetime.timedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT),
                (date + datetime.timedelta(days=2)).strftime(DEFAULT_SERVER_DATE_FORMAT),
                (date + datetime.timedelta(days=3)).strftime(DEFAULT_SERVER_DATE_FORMAT),
                (date + datetime.timedelta(days=4)).strftime(DEFAULT_SERVER_DATE_FORMAT),
                (date + datetime.timedelta(days=5)).strftime(DEFAULT_SERVER_DATE_FORMAT),
                datetmp[1],
            ]]
        return result

    def get_market(self, form):
        where_str = ''
        if form['inv_state'] == 'draft':
            where_str = ''' WHERE inv.state = 'draft' AND inv.type = 'out_invoice' '''
        else:
            if form['inv_state'] != 'all':
                where_str = ''' WHERE inv.state = '%s' AND inv.type = 'out_invoice' '''%form['inv_state']
            else:
                where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['partner_id']:
            where_str = '%s %s'%(where_str, ' AND inv.partner_id = %s'%form['partner_id'][0])

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])
        select_str = """
                 SELECT
                        distinct (categ.id) as id,
                        categ.name,
                        part.city
                FROM ( account_invoice inv
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                GROUP BY categ.name,categ.id, part.city
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

    def get_customer(self, form, state_id, week):
        where_str = ''
        if form['inv_state'] == 'draft':
            where_str = ''' WHERE inv.state = 'draft' AND inv.type = 'out_invoice'  '''
        else:
            if form['inv_state'] != 'all':
                where_str = ''' WHERE inv.state = '%s' AND inv.type = 'out_invoice'  '''%form['inv_state']
            else:
                where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['partner_id']:
            where_str = '%s %s'%(where_str, ' AND inv.partner_id = %s'%form['partner_id'][0])

        if week:
            week = ' , '.join(map(lambda x: " '%s' " %x, week))
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date in (%s) '''%week)
        else:
            if form['date_from']:
                where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

            if form['date_to']:
                where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])

        if state_id:
            if state_id['id']:
                where_str = '%s %s'%(where_str, ''' AND categ.id = %s '''%state_id['id'])
            else:
                where_str = '%s %s'%(where_str, ''' AND categ.id is null''')

        sql = '''
                 SELECT
                        distinct (part.id) as id,
                        part.name
                FROM ( account_invoice inv
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                GROUP BY part.name,part.id
                order by part.name
        '''%where_str
        self.cr.execute(sql)
        res = self.cr.dictfetchall()
        return res

    def get_product(self, form, state_id, partner, week):
        where_str = ''
        where_full_str = ''
        if form['inv_state'] == 'draft':
            where_str = ''' WHERE inv.state = 'draft' AND inv.type = 'out_invoice'  '''
        else:
            if form['inv_state'] != 'all':
                where_str = ''' WHERE inv.state = '%s' AND inv.type = 'out_invoice'  '''%form['inv_state']
            else:
                where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if partner:
            where_str = '%s %s'%(where_str, ' AND inv.partner_id = %s'%partner['id'])
        elif form['partner_id']:
            where_str = '%s %s'%(where_str, ' AND inv.partner_id = %s'%form['partner_id'][0])

        if state_id:
            if state_id['id']:
                where_str = '%s %s'%(where_str, ''' AND categ.id = %s '''%state_id['id'])
            else:
                where_str = '%s %s'%(where_str, ''' AND categ.id is null''')

        if week:
            week = ' , '.join(map(lambda x: " '%s' " %x, week))
            where_full_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date in (%s) '''%week)
        else:
            if form['date_from']:
                where_full_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

            if form['date_to']:
                where_full_str = '%s %s'%(where_full_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])

        select_str = """
                 SELECT
                        distinct(ivl.product_id) as product_id
                FROM (
                    account_invoice inv
                    join account_invoice_line ivl on (ivl.invoice_id = inv.id)
                    join res_partner part on (inv.partner_id=part.id)
                    left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                    left join res_partner_category categ on (rel.category_id=categ.id))
                %s

        """%where_full_str
        self.cr.execute(select_str)
        list_product = self.cr.dictfetchall()
        result = []
        no = 0
        for product in list_product:
            no += 1
            product_name = self.product(product['product_id'])
            select_str = """
                     SELECT
                            sum(ivl.product_uos_qty) as unit_qty,
                            sum(ivl.quantity) as kg_qty,
                            inv.date_invoice::date
                    FROM (
                        account_invoice inv
                        join account_invoice_line ivl on (ivl.invoice_id = inv.id)
                        join res_partner part on (inv.partner_id=part.id)
                        left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                        left join res_partner_category categ on (rel.category_id=categ.id))
                    %s
                    AND ivl.product_id = %s

                    GROUP BY inv.date_invoice
            """%(where_full_str, product['product_id'])
            self.cr.execute(select_str)
            res = self.cr.dictfetchall()
            dict_date = {}
            for tmp in res:
                count = 1
                date = datetime.datetime.strptime(tmp['date_invoice'], DEFAULT_SERVER_DATE_FORMAT)
                date_old_qty = []
                while count <= 4:
                    count += 1
                    date = date - datetime.timedelta(days=7)
                    date_old_qty += ['%s'%date.strftime(DEFAULT_SERVER_DATE_FORMAT)]
                select_str = """
                             SELECT
                                    sum(ivl.product_uos_qty) as unit_qty,
                                    sum(ivl.quantity) as kg_qty
                            FROM (
                                account_invoice inv
                                join account_invoice_line ivl on (ivl.invoice_id = inv.id)
                                join res_partner part on (inv.partner_id=part.id)
                                left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                                left join res_partner_category categ on (rel.category_id=categ.id))
                            %s
                            AND ivl.product_id = %s

                     """%('%s %s'%(where_str, ''' AND inv.date_invoice::date in %s '''%str(tuple(date_old_qty))), \
                            product['product_id'])
                self.cr.execute(select_str)
                old = self.cr.dictfetchone()
                old_qty = 0
                if old and old['unit_qty']:
                    old_qty += old['unit_qty']
                dict_date.update({tmp['date_invoice']: [round(old_qty/4, 2), tmp['unit_qty']]})

            result.append({
                'name': product_name,
                'no': no,
                'quantity': dict_date
            })

        return result

    def get_qty(self, dict_qty, date):
        return dict_qty.get(date, [0,0])

    def product(self, prod_id):
        res = self.pool.get('product.product').name_get(self.cr, self.uid, [prod_id])
        return res and res[0] and res[0][1] or self.pool.get('product.product').browse(self.cr, self.uid, prod_id).name





