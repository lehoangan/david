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
            'get_client': self.get_client,
            'get_total_market': self.get_total_market,
            'get_client_product': self.get_client_product,
            'get_total_all': self.get_total_all,
        })

    def get_market(self, form):
        where_str_vou = ''' WHERE vou.state not in ('draft', 'cancel') AND vou.type = 'receipt' '''
        where_previous = ''

        if form['date_from']:
            where_str_vou = '%s %s'%(where_str_vou, ''' AND vou.date::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str_vou = '%s %s'%(where_str_vou, ''' AND vou.date::date <= '%s' '''%form['date_to'])

        if form['tag_ids']:
            tag_ids = form['tag_ids']
            if tag_ids:
                tag_ids += [-1,-1]
            where_str_vou = '%s %s'%(where_str_vou, ''' AND categ.id in %s '''%str(tuple(tag_ids)))
            where_previous = ''' AND categ.id in %s '''%str(tuple(tag_ids))

        where_str = ''' WHERE inv.state not in ('refund', 'cancel') AND inv.type = 'out_invoice' '''

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])

        if form['tag_ids']:
            tag_ids = form['tag_ids']
            if tag_ids:
                tag_ids += [-1,-1]
            where_str = '%s %s'%(where_str, ''' AND categ.id in %s '''%str(tuple(tag_ids)))

        select_str = """
                 SELECT id, name, sum(payment) as payment
                 FROM
                     ((SELECT
                            distinct (categ.id) as id,
                            categ.name,
                            sum(vou.amount) as payment
                    FROM ( account_voucher vou
                              join res_partner part on (vou.partner_id=part.id)
                              left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                              left join res_partner_category categ on (rel.category_id=categ.id))
                    %s
                    GROUP BY categ.name,categ.id
                    order by categ.name)
                    UNION
                    (SELECT
                            distinct (categ.id) as id,
                            categ.name,
                            0 as payment
                    FROM ( account_invoice inv
                              join res_partner part on (inv.partner_id=part.id)
                              left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                              left join res_partner_category categ on (rel.category_id=categ.id))
                    %s
                    GROUP BY categ.name,categ.id
                    order by categ.name)
                    UNION
                     ( SELECT distinct (id) as id, name, payment FROM (
                         SELECT SUM(l.debit-l.credit) as payment, categ.id, categ.name
                              FROM account_move_line l
                                  JOIN account_account a ON (l.account_id=a.id)
                                  join res_partner part on (l.partner_id=part.id)
                                  left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                                  left join res_partner_category categ on (rel.category_id=categ.id)
                              WHERE a.type = 'receivable'
                              AND l.reconcile_id IS NULL
                              AND l.partner_id IS NOT NULL
                              AND l.state <> 'draft' AND l.date < '%s' %s
                              GROUP BY categ.id, categ.name)as opening WHERE payment > 0)
                     ) as TEMP
                    GROUP BY name,id
                ORDER BY name
        """%(where_str_vou, where_str, form['date_from'], where_previous)
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        for categ in res:
            if not categ['id']: continue
            result = self.pool.get('res.partner.category').name_get(self.cr, self.uid, categ['id'])
            if result and result[0]:
                categ['name'] = result[0][1]
        return res

    def _get_opening_client(self, form, tag):
        where_str_vou = ''' WHERE vou.state not in ('draft', 'cancel') AND vou.type = 'receipt' '''
        where_previous = ''

        if form['date_from']:
            where_str_vou = '%s %s' % (where_str_vou, ''' AND vou.date::date < '%s' ''' % form['date_from'])

        if tag:
            if tag['id']:
                where_str_vou = '%s %s' % (where_str_vou, ''' AND categ.id = %s ''' % tag['id'])
                where_previous = ''' AND categ.id = %s ''' % tag['id']
            else:
                where_str_vou = '%s %s' % (where_str_vou, ''' AND categ.id is null''')
                where_previous = ' AND categ.id is null'

        where_str = ''' WHERE inv.state not in ('refund', 'cancel') AND inv.type = 'out_invoice' '''

        if form['date_from']:
            where_str = '%s %s' % (where_str, ''' AND inv.date_invoice::date < '%s' ''' % form['date_from'])

        if tag:
            if tag['id']:
                where_str = '%s %s' % (where_str, ''' AND categ.id = %s ''' % tag['id'])
            else:
                where_str = '%s %s' % (where_str, ''' AND categ.id is null''')

        select_str = """
                 SELECT distinct (id) as id
                 FROM
                     ((SELECT
                            distinct (part.id) as id
                    FROM ( account_voucher vou
                              join res_partner part on (vou.partner_id=part.id)
                              left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                              left join res_partner_category categ on (rel.category_id=categ.id))
                    %s)
                    UNION
                    (SELECT
                            distinct (part.id) as id
                    FROM ( account_invoice inv
                              join res_partner part on (inv.partner_id=part.id)
                              left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                              left join res_partner_category categ on (rel.category_id=categ.id))
                    %s
                    )
                     UNION
                     ( SELECT partner_id as id FROM (
                         SELECT SUM(l.debit-l.credit) as amount, l.partner_id
                              FROM account_move_line l
                                  JOIN account_account a ON (l.account_id=a.id)
                                  join res_partner part on (l.partner_id=part.id)
                                  left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                                  left join res_partner_category categ on (rel.category_id=categ.id)
                              WHERE a.type = 'receivable'
                              AND l.reconcile_id IS NULL
                              AND l.partner_id IS NOT NULL
                              AND l.state <> 'draft' AND l.date < '%s' %s
                              GROUP BY l.partner_id)as opening WHERE amount > 0)
                     ) as TEMP
        """ % (where_str_vou, where_str, form['date_from'], where_previous)

        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        result ={}
        for part in res:
            if not part['id']: continue

            # get amount of in transact sale
            # get amount of discount
            in_vwhere_str = ''' WHERE inv.state not in ('refund', 'cancel') AND inv.type = 'out_invoice' AND inv.partner_id=%s ''' % \
                            part['id']

            if form['date_from']:
                in_vwhere_str = '%s %s' % (in_vwhere_str, ''' AND inv.date_invoice::date < '%s' ''' % form['date_from'])

            sql = '''
                SELECT
                        sum(l.quantity * l.price_unit * l.discount / 100.0) as disc_percent_amount,
                        sum(l.discount_kg * l.price_unit * (100.0-l.discount) / 100.0 + l.quantity * l.price_unit * l.discount / 100.0) as disc_amount,
                        sum(l.discount_kg * l.price_unit * (100.0-l.discount) / 100.0) as disc_kg_amount,
                        SUM(l.quantity * l.price_unit) as amount

                FROM (
                       account_invoice_line l
                          join account_invoice inv on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
            ''' % in_vwhere_str
            self.cr.execute(sql)
            discount = self.cr.dictfetchone()
            disc_percent_amount = discount['disc_percent_amount'] or 0
            disc_kg_amount = discount['disc_kg_amount'] or 0
            amount_in_period = discount['amount'] or 0
            part.update({
                'percent_amount': disc_percent_amount,
                'kg_amount': disc_kg_amount,
                'sale_amount': amount_in_period
            })
            # payment information
            where_str_vou = ''' WHERE vou.state not in ('draft', 'cancel') AND vou.type = 'receipt' AND vou.partner_id=%s ''' % \
                            part['id']

            if form['date_from']:
                where_str_vou = '%s %s' % (where_str_vou, ''' AND vou.date::date < '%s' ''' % form['date_from'])
            select_str = """
                SELECT
                        vou.id
                FROM account_voucher vou
                %s
            """ % where_str_vou
            self.cr.execute(select_str)
            res1 = self.cr.dictfetchall()
            total = 0
            diff = 0
            for vou in res1:
                if not vou['id']: continue
                value = self.get_amount_due(vou['id'])
                total += value[0]
                diff += value[1]
            part.update({
                'payment': total,
                'diff': diff,
            })
            # ending

            ending = part['sale_amount'] - part['percent_amount'] - part['kg_amount'] - part[
                'payment'] + part['diff']

            part.update({
                'ending': ending
            })
            result.update({part['id']: ending})
        return result

    def get_client(self, form, tag):
        opening = self._get_opening_client(form, tag)
        where_str_vou = ''' WHERE vou.state not in ('draft', 'cancel') AND vou.type = 'receipt' '''
        where_previous = ''

        if form['date_from']:
            where_str_vou = '%s %s'%(where_str_vou, ''' AND vou.date::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str_vou = '%s %s'%(where_str_vou, ''' AND vou.date::date <= '%s' '''%form['date_to'])

        if tag:
            if tag['id']:
                where_str_vou = '%s %s'%(where_str_vou, ''' AND categ.id = %s '''%tag['id'])
                where_previous = ''' AND categ.id = %s '''%tag['id']
            else:
                where_str_vou = '%s %s'%(where_str_vou, ''' AND categ.id is null''')
                where_previous = ' AND categ.id is null'

        where_str = ''' WHERE inv.state not in ('refund', 'cancel') AND inv.type = 'out_invoice' '''

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])

        if tag:
            if tag['id']:
                where_str = '%s %s'%(where_str, ''' AND categ.id = %s '''%tag['id'])
            else:
                where_str = '%s %s'%(where_str, ''' AND categ.id is null''')

        select_str = """
                 SELECT distinct (id) as id
                 FROM
                     ((SELECT
                            distinct (part.id) as id
                    FROM ( account_voucher vou
                              join res_partner part on (vou.partner_id=part.id)
                              left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                              left join res_partner_category categ on (rel.category_id=categ.id))
                    %s)
                    UNION
                    (SELECT
                            distinct (part.id) as id
                    FROM ( account_invoice inv
                              join res_partner part on (inv.partner_id=part.id)
                              left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                              left join res_partner_category categ on (rel.category_id=categ.id))
                    %s
                    )
                     UNION
                     ( SELECT partner_id as id FROM (
                         SELECT SUM(l.debit-l.credit) as amount, l.partner_id
                              FROM account_move_line l
                                  JOIN account_account a ON (l.account_id=a.id)
                                  join res_partner part on (l.partner_id=part.id)
                                  left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                                  left join res_partner_category categ on (rel.category_id=categ.id)
                              WHERE a.type = 'receivable'
                              AND l.reconcile_id IS NULL
                              AND l.partner_id IS NOT NULL
                              AND l.state <> 'draft' AND l.date < '%s' %s
                              GROUP BY l.partner_id)as opening WHERE amount > 0)
                     ) as TEMP
        """%(where_str_vou, where_str, form['date_from'], where_previous)

        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        for part in res:
            if not part['id']: continue
            if form['date_from']:
                result = self.pool.get('res.partner').browse(self.cr, self.uid, part['id'], {'date_to': form['date_from']})
                part.update({
                    'name': result.name,
                    'opening': opening.get(part['id'], 0)
                })

            #get amount of in transact sale
            #get amount of discount
            in_vwhere_str = ''' WHERE inv.state not in ('refund', 'cancel') AND inv.type = 'out_invoice' AND inv.partner_id=%s '''%part['id']

            if form['date_from']:
                in_vwhere_str = '%s %s'%(in_vwhere_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

            if form['date_to']:
                in_vwhere_str = '%s %s'%(in_vwhere_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])

            sql = '''
                SELECT
                        sum(l.quantity * l.price_unit * l.discount / 100.0) as disc_percent_amount,
                        sum(l.discount_kg * l.price_unit * (100.0-l.discount) / 100.0 + l.quantity * l.price_unit * l.discount / 100.0) as disc_amount,
                        sum(l.discount_kg * l.price_unit * (100.0-l.discount) / 100.0) as disc_kg_amount,
                        SUM(l.quantity * l.price_unit) as amount

                FROM (
                       account_invoice_line l
                          join account_invoice inv on (l.invoice_id=inv.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s
            '''%in_vwhere_str
            self.cr.execute(sql)
            discount = self.cr.dictfetchone()
            disc_percent_amount = discount['disc_percent_amount'] or 0
            disc_kg_amount = discount['disc_kg_amount'] or 0
            amount_in_period = discount['amount'] or 0
            part.update({
                    'percent_amount': disc_percent_amount,
                    'percent': amount_in_period and round(disc_percent_amount/amount_in_period*100, 2) or 0,
                    'kg_amount': disc_kg_amount,
                    'kg_percent': amount_in_period and round(disc_kg_amount/amount_in_period*100, 2) or 0,
                    'sale_amount': amount_in_period
                })
            #payment information
            where_str_vou = ''' WHERE vou.state not in ('draft', 'cancel') AND vou.type = 'receipt' AND vou.partner_id=%s '''%part['id']

            if form['date_from']:
                where_str_vou = '%s %s'%(where_str_vou, ''' AND vou.date::date >= '%s' '''%form['date_from'])

            if form['date_to']:
                where_str_vou = '%s %s'%(where_str_vou, ''' AND vou.date::date <= '%s' '''%form['date_to'])
            select_str = """
                SELECT
                        vou.id
                FROM account_voucher vou
                %s
            """%where_str_vou
            if part['id'] == 400:
                print select_str
            self.cr.execute(select_str)
            res1 = self.cr.dictfetchall()
            total = 0
            diff = 0
            for vou in res1:
                if not vou['id']: continue
                value = self.get_amount_due(vou['id'])
                total += value[0]
                diff += value[1]
            part.update({
                'payment': total,
                'percent_payment': (amount_in_period + part['opening']) and round(total/(amount_in_period + part['opening'])*100, 2) or 0,
                'diff': diff,
            })
            if part['id'] == 400:
                print part['diff']
            #ending

            ending = part['opening'] + part['sale_amount'] - part['percent_amount'] - part['kg_amount'] - part['payment'] + part['diff']

            part.update({
                'percent_ending': part['sale_amount'] and round(ending/part['sale_amount']*100, 2) or 0,
                'ending': ending
            })
        return res

    def get_client_product(self, form, part):
        if form['type'] == 'client':
            return []
        #get amount of discount
        in_vwhere_str = ''' WHERE inv.state not in ('refund', 'cancel') AND inv.type = 'out_invoice' AND inv.partner_id=%s '''%part['id']

        if form['date_from']:
            in_vwhere_str = '%s %s'%(in_vwhere_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            in_vwhere_str = '%s %s'%(in_vwhere_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])

        sql = '''
            SELECT
                    l.product_id,
                    sum(l.quantity * l.price_unit) as sale_amount,
                    --sum((l.quantity-l.discount_kg) * l.price_unit * (100.0-l.discount) / 100.0) as sale_amount,
                    sum(l.quantity * l.price_unit * l.discount / 100.0) as percent_amount,
                    sum(l.discount_kg * l.price_unit * (100.0-l.discount) / 100.0 + l.quantity * l.price_unit * l.discount / 100.0) as disc_amount,
                    sum(l.discount_kg * l.price_unit * (100.0-l.discount) / 100.0) as kg_amount

            FROM (
                   account_invoice_line l
                      join account_invoice inv on (l.invoice_id=inv.id)
                      join res_partner part on (inv.partner_id=part.id)
                      left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                      left join res_partner_category categ on (rel.category_id=categ.id))
            %s
            GROUP BY l.product_id
        '''%in_vwhere_str
        self.cr.execute(sql)
        res = self.cr.dictfetchall()
        for discount in res:
            res_name = self.pool.get('product.product').name_get(self.cr, self.uid, discount['product_id'])
            name = res_name and res_name[0] and res_name[0][1] or self.pool.get('product.product').browse(self.cr, self.uid, discount['product_id']).name
            discount.update({
                    'name': name,
                    'percent': discount['sale_amount'] and round(discount['percent_amount']/discount['sale_amount']*100, 2) or 0,
                    'kg_percent': discount['sale_amount'] and round(discount['kg_amount']/discount['sale_amount']*100, 2) or 0,
                })
        return res

    def get_amount_due(self, voucher_id):
        voucher_obj = self.pool.get('account.voucher')
        voucher = voucher_obj.browse(self.cr, self.uid, voucher_id)
        amount = voucher.amount
        diff = 0
        if voucher.payment_option == 'with_writeoff':
            diff = voucher.writeoff_amount
        # for line in voucher.line_cr_ids:
        #     amount += line.amount_unreconciled - line.amount
        return amount, diff

    def get_total_market(self, form, tag):
        res = {'opening': 0,
               'sale_amount': 0,
               'percent_amount': 0,
               'percent': 0,
               'kg_amount': 0,
               'kg_percent': 0,
               'payment': 0,
               'percent_payment': 0,
               'diff': 0,
               'percent_ending': 0,
               'ending': 0,
               }
        details = self.get_client(form, tag)
        for line in details:
            res['opening'] += line['opening']
            res['sale_amount'] += line['sale_amount']
            res['percent_amount'] += line['percent_amount']
            res['kg_amount'] += line['kg_amount']
            res['payment'] += line['payment']
            res['diff'] += line['diff']
            res['ending'] += line['ending']
        res['percent'] = res['sale_amount'] and round(res['percent_amount']/res['sale_amount']*100,2) or 0
        res['kg_percent'] = res['sale_amount'] and round(res['kg_amount']/res['sale_amount']*100,2) or 0
        res['percent_payment'] = (res['sale_amount']+res['opening']) and round(res['payment']/(res['sale_amount']+res['opening'])*100,2) or 0
        res['percent_ending'] = res['sale_amount'] and round(res['ending']/res['sale_amount']*100,2) or 0
        return [res]

    def get_total_all(self, form):
        markets = self.get_market(form)
        res = {'opening': 0,
               'sale_amount': 0,
               'percent_amount': 0,
               'percent': 0,
               'kg_amount': 0,
               'kg_percent': 0,
               'payment': 0,
               'percent_payment': 0,
               'diff': 0,
               'percent_ending': 0,
               'ending': 0,
               }
        for tag in markets:
            details = self.get_client(form, tag)
            for line in details:
                res['opening'] += line['opening']
                res['sale_amount'] += line['sale_amount']
                res['percent_amount'] += line['percent_amount']
                res['kg_amount'] += line['kg_amount']
                res['payment'] += line['payment']
                res['diff'] += line['diff']
                res['ending'] += line['ending']
            res['percent'] += res['sale_amount'] and round(res['percent_amount']/res['sale_amount']*100,2) or 0
            res['kg_percent'] += res['sale_amount'] and round(res['kg_amount']/res['sale_amount']*100,2) or 0
            res['percent_payment'] += (res['sale_amount']+res['opening']) and round(res['payment']/(res['sale_amount']+res['opening'])*100,2) or 0
            res['percent_ending'] += res['sale_amount'] and round(res['ending']/res['sale_amount']*100,2) or 0
        return [res]



