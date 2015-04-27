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
            'get_total' : self.get_total,
        })

    def get_market(self, form):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE inv.state = 'draft' AND inv.type = 'out_invoice' '''
        else:
            where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['partner_id']:
            where_str = '%s %s'%(where_str, ' AND inv.partner_id = %s'%form['partner_id'][0])

        if form['date']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date = '%s' '''%form['date'])

        select_str = """
                 SELECT
                        distinct (categ.id) as id,
                        categ.name,
                        part.city,
                        sum(invl.discount_kg) as disc_kg,
                        sum(invl.discount * invl.price_unit) as disc
                FROM (
                    account_invoice_line invl
                    join account_invoice inv on (invl.invoice_id = inv.id)
                    join sale_order_invoice_rel inv_rel on (inv_rel.invoice_id=inv.id)
                          join sale_order s on (inv_rel.order_id=s.id)
                          join res_partner part on (inv.partner_id=part.id)
                          join product_pricelist pl on (s.pricelist_id = pl.id)

                          left join res_users follow on (part.payment_responsible_id=follow.id)
                          left join res_partner follower on (follow.partner_id=follower.id)

                          left join res_users us on (inv.user_id=us.id)
                          left join res_partner part2 on (us.partner_id=part2.id)

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

    def get_detail(self, form, state_id):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE inv.state = 'draft' AND inv.type = 'out_invoice'  '''
        else:
            where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['partner_id']:
            where_str = '%s %s'%(where_str, ' AND inv.partner_id = %s'%form['partner_id'][0])

        if form['date']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date = '%s' '''%form['date'])

        if state_id:
            if state_id['id']:
                where_str = '%s %s'%(where_str, ''' AND categ.id = %s '''%state_id['id'])
            else:
                where_str = '%s %s'%(where_str, ''' AND categ.id is null''')

        select_str = """
                 SELECT
                        part.id as client_id,
                        part.name as client,
                        part2.name as saleman,
                        pl.name as pricelist,
                        pl.id as pricelist_id,
                        follower.name as follow,
                        sum(invl.discount_kg) as disc_kg,
                        sum(invl.discount * invl.price_unit) as disc
                FROM (
                    account_invoice_line invl
                    join account_invoice inv on (invl.invoice_id = inv.id)
                    join sale_order_invoice_rel inv_rel on (inv_rel.invoice_id=inv.id)
                          join sale_order s on (inv_rel.order_id=s.id)
                          join res_partner part on (inv.partner_id=part.id)
                          join product_pricelist pl on (s.pricelist_id = pl.id)

                          left join res_users follow on (part.payment_responsible_id=follow.id)
                          left join res_partner follower on (follow.partner_id=follower.id)

                          left join res_users us on (inv.user_id=us.id)
                          left join res_partner part2 on (us.partner_id=part2.id)

                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s

                GROUP BY
                        part.id,
                        part.name,
                        part2.name,
                        pl.name,
                        pl.id,
                        follower.name
                order by part.name
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        invoice_obj = self.pool.get('res.partner')
        result = {}
        no = 1
        for inv in res:
            obj = invoice_obj.browse(self.cr, self.uid, inv['client_id'])
            inv.update({'limit_credit': obj.credit,
                        'term': obj.property_payment_term and obj.property_payment_term.name or '',
                        'no': no,
                    })
            no += 1
        # result = sorted(result, key=lambda k: k['no'])
        return res

    def get_total(self, form):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE inv.state = 'draft' AND inv.type = 'out_invoice'  '''
        else:
            where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['partner_id']:
            where_str = '%s %s'%(where_str, ' AND inv.partner_id = %s'%form['partner_id'][0])

        if form['date']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date = '%s' '''%form['date'])

        select_str = """
                 SELECT
                        sum(invl.discount_kg) as disc_kg,
                        sum(invl.discount * invl.price_unit) as disc
                FROM (
                    account_invoice_line invl
                    join account_invoice inv on (invl.invoice_id = inv.id)
                    join sale_order_invoice_rel inv_rel on (inv_rel.invoice_id=inv.id)
                          join sale_order s on (inv_rel.order_id=s.id)
                          join res_partner part on (inv.partner_id=part.id)
                          join product_pricelist pl on (s.pricelist_id = pl.id)

                          left join res_users follow on (part.payment_responsible_id=follow.id)
                          left join res_partner follower on (follow.partner_id=follower.id)

                          left join res_users us on (inv.user_id=us.id)
                          left join res_partner part2 on (us.partner_id=part2.id)

                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s

        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res


    


