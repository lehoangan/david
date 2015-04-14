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
            'get_customer': self.get_customer,
            'get_detail': self.get_detail,
            'get_amount_due': self.get_amount_due,
            'get_market': self.get_market,
        })

    def get_market(self, form):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE vou.state = 'draft' AND vou.type = 'receipt' '''
        else:
            where_str = ''' WHERE vou.state not in ('draft', 'cancel') AND vou.type = 'receipt' '''

        if form['partner_id']:
            where_str = '%s %s'%(where_str, ' AND vou.partner_id = %s'%form['partner_id'][0])

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND vou.date::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND vou.date::date <= '%s' '''%form['date_to'])
        select_str = """
                 SELECT
                        distinct (categ.id) as id,
                        categ.name,
                        part.city
                FROM ( account_voucher vou
                          join res_partner part on (vou.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                GROUP BY categ.name,categ.id, part.city
                order by categ.name
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        print select_str
        for categ in res:
            if not categ['id']: continue
            result = self.pool.get('res.partner.category').name_get(self.cr, self.uid, categ['id'])
            if result and result[0]:
                categ['name'] = result[0][1]
        return res

    def total_customer(self, form, partner_id):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE inv.state = 'draft' AND inv.type = 'out_invoice' AND inv.partner_id=%s '''%partner_id
        else:
            where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' AND inv.partner_id=%s '''%partner_id

        if form['partner_id']:
            where_str = '%s %s'%(where_str, ' AND inv.partner_id = %s'%form['partner_id'][0])

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])
        select_str = """
                 SELECT
                        distinct (inv.id) as id
                FROM ( account_invoice inv
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
        """%where_str
        self.cr.execute(select_str)
        res1 = self.cr.dictfetchall()

        sql = '''
            SELECT
                sum(quantity) as quantity,
                sum(discount_kg) as disc_kg,
                sum(price_unit * ((100 -discount)/100)) as disc_amount
            FROM
                account_invoice_line
            WHERE
                invoice_id in (%s)
        '''%select_str
        self.cr.execute(sql)
        res = self.cr.dictfetchall()

        invoice_obj = self.pool.get('account.invoice')
        total,residual = 0,0
        for inv in res1:
            obj = invoice_obj.browse(self.cr, self.uid, inv['id'])
            total += obj.amount_total
            if obj.state in ('open', 'paid'):
                residual += obj.residual
            else:
                residual += obj.amount_total

        res[0].update({'amount': total,
                    'paid': total - residual,
                    'remain': residual,
                    })
        return res

    def get_customer(self, form, state_id):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE vou.state = 'draft' AND vou.type = 'receipt'  '''
        else:
            where_str = ''' WHERE vou.state not in ('draft', 'cancel') AND vou.type = 'receipt' '''

        if form['partner_id']:
            where_str = '%s %s'%(where_str, ' AND vou.partner_id = %s'%form['partner_id'][0])

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND vou.date::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND vou.date::date <= '%s' '''%form['date_to'])

        if state_id:
            if state_id['id']:
                where_str = '%s %s'%(where_str, ''' AND categ.id = %s '''%state_id['id'])
            else:
                where_str = '%s %s'%(where_str, ''' AND categ.id is null''')

        sql = '''
                 SELECT
                        distinct (part.id) as id,
                        part.name
                FROM ( account_voucher vou
                          join res_partner part on (vou.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                GROUP BY part.name,part.id
                order by part.name
        '''%where_str
        self.cr.execute(sql)
        res = self.cr.dictfetchall()
        # for client in res:
        #     value = self.total_customer(form, client['id'])
        #     if value and value[0]:
        #         client.update(value[0])
        return res

    def get_detail(self, form, state_id, partner):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE vou.state = 'draft' AND vou.type = 'receipt'  '''
        else:
            where_str = ''' WHERE vou.state not in ('draft', 'cancel') AND vou.type = 'receipt' '''

        if partner:
            where_str = '%s %s'%(where_str, ' AND vou.partner_id = %s'%partner['id'])
        elif form['partner_id']:
            where_str = '%s %s'%(where_str, ' AND vou.partner_id = %s'%form['partner_id'][0])

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND vou.date::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND vou.date::date <= '%s' '''%form['date_to'])

        if state_id:
            if state_id['id']:
                where_str = '%s %s'%(where_str, ''' AND categ.id = %s '''%state_id['id'])
            else:
                where_str = '%s %s'%(where_str, ''' AND categ.id is null''')

        select_str = """
                 SELECT
                        ROW_NUMBER() OVER(ORDER BY vou.id) AS no,
                        vou.id,
                        vou.name as memo,
                        vou.number,
                        vou.date,
                        vou.amount,
                        vou.reference as ref,
                        part2.name as user
                FROM (
                    account_voucher vou
                      join res_partner part on (vou.partner_id=part.id)
                      join res_users us on (vou.create_uid=us.id)
                      join res_partner part2 on (us.partner_id=part2.id)
                      left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                      left join res_partner_category categ on (rel.category_id=categ.id))
                %s

        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        return res

    def get_amount_due(self, voucher_id):
        voucher_obj = self.pool.get('account.voucher')
        voucher = voucher_obj.browse(self.cr, self.uid, voucher_id)
        amount = 0
        for line in voucher.line_cr_ids:
            amount += line.amount_unreconciled - line.amount
        return amount

    def total(self, form):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE vou.state = 'draft' AND vou.type = 'receipt'  '''
        else:
            where_str = ''' WHERE vou.state not in ('draft', 'cancel') AND vou.type = 'receipt' '''

        if form['partner_id']:
            where_str = '%s %s'%(where_str, ' AND vou.partner_id = %s'%form['partner_id'][0])

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND vou.date::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND vou.date::date <= '%s' '''%form['date_to'])
        select_str = """
                 SELECT
                        distinct (vou.id) as id
                FROM ( account_voucher vou
                          join res_partner part on (vou.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
        """%where_str
        self.cr.execute(select_str)
        res1 = self.cr.dictfetchall()

        sql = '''
            SELECT
                sum(quantity) as quantity,
                sum(discount_kg) as disc_kg,
                sum(price_unit * ((100 -discount)/100)) as disc_amount
            FROM
                account_voucher_line
            WHERE
                invoice_id in (%s)
        '''%select_str
        self.cr.execute(sql)
        res = self.cr.dictfetchall()

        invoice_obj = self.pool.get('account.invoice')
        total,residual = 0,0
        for vou in res1:
            obj = invoice_obj.browse(self.cr, self.uid, vou['id'])
            total += obj.amount_total

            if obj.state in ('open', 'paid'):
                residual += obj.residual
            else:
                residual += obj.amount_total

        res[0].update({'amount': total,
                    'paid': total - residual,
                    'remain': residual,
                    })
        return res
    


