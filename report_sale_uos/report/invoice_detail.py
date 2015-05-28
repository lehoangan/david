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
            'get_invoice': self.get_invoice,
            'total': self.total,
            'get_market': self.get_market,
        })

    def get_market(self, form):
        where_str = ''
        if form['state'] == 'draft':
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

    def total_customer(self, form, partner_id):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE inv.state = 'draft' AND inv.type = 'out_invoice' AND inv.partner_id=%s '''%partner_id
        else:
            if form['inv_state'] != 'all':
                where_str = ''' WHERE inv.state = '%s' AND inv.type = 'out_invoice' AND inv.partner_id=%s '''%(form['inv_state'], partner_id)
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
            where_str = ''' WHERE inv.state = 'draft' AND inv.type = 'out_invoice'  '''
        else:
            if form['inv_state'] != 'all':
                where_str = ''' WHERE inv.state = '%s' AND inv.type = 'out_invoice'  '''%form['inv_state']
            else:
                where_str = ''' WHERE inv.state not in ('draft', 'cancel') AND inv.type = 'out_invoice' '''

        if form['partner_id']:
            where_str = '%s %s'%(where_str, ' AND inv.partner_id = %s'%form['partner_id'][0])

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
        for client in res:
            value = self.total_customer(form, client['id'])
            if value and value[0]:
                client.update(value[0])
        return res

    def get_invoice(self, form, state_id, partner):
        where_str = ''
        if form['state'] == 'draft':
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

        if form['date_from']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date >= '%s' '''%form['date_from'])

        if form['date_to']:
            where_str = '%s %s'%(where_str, ''' AND inv.date_invoice::date <= '%s' '''%form['date_to'])

        if state_id:
            if state_id['id']:
                where_str = '%s %s'%(where_str, ''' AND categ.id = %s '''%state_id['id'])
            else:
                where_str = '%s %s'%(where_str, ''' AND categ.id is null''')

        select_str = """
                 SELECT
                        inv.id,
                        s.name,
                        inv.number,
                        inv.date_invoice
                FROM (
                    account_invoice inv
                    join sale_order_invoice_rel inv_rel on (inv_rel.invoice_id=inv.id)
                          join sale_order s on (inv_rel.order_id=s.id)
                          join res_partner part on (inv.partner_id=part.id)
                          left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                          left join res_partner_category categ on (rel.category_id=categ.id))
                %s

                order by inv.date_invoice desc
        """%where_str
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        invoice_obj = self.pool.get('account.invoice')
        result = {}
        no = 1
        for inv in res:
            obj = invoice_obj.browse(self.cr, self.uid, inv['id'])
            if inv['id'] not in result.keys():
                total = obj.amount_total
                residual = obj.amount_total
                if obj.state in ('open', 'paid'):
                    residual = obj.residual
                qty,disc_kg,disc_amount = 0,0,0
                for line in obj.invoice_line:
                    qty += line.quantity
                    disc_kg += line.discount_kg
                    disc_amount += line.price_unit * (1-(line.discount or 0)/100)
                    
                inv.update({'amount': total,
                            'paid': total - residual,
                            'remain': residual,
                            'invoice': obj,
                            'no': no,
                            'qty': qty,
                            'disc_kg': disc_kg,
                            'disc_amount': disc_amount,
                        })
                result.update({inv['id']: inv})
                no += 1
            else:
                result[inv['id']]['name'] = '%s - %s'%(result[inv['id']]['name'], inv['name'])
        result = result.values()
        result = sorted(result, key=lambda k: k['date_invoice'])
        if result:
            result.reverse()
            for i in range(0, len(result)):
                result[i]['no'] = i + 1
        return result

    def get_detail(self, form, inv):
        res = []
        no = 1
        for line in inv.invoice_line:
            prod = line.product_id.name_get()
            res.append({
                'no': no,
                'prod': prod and prod[0] and prod[0][1] or line.product_id.name,
                'qty': line.quantity,
                'price': line.price_unit,
                'disc_kg': line.discount_kg,
                'disc_amount': line.price_unit * (1-(line.discount or 0)/100),
                'amount': line.price_subtotal,
            })
            no += 1
        return res

    def total(self, form):
        where_str = ''
        if form['state'] == 'draft':
            where_str = ''' WHERE inv.state = 'draft' AND inv.type = 'out_invoice'  '''
        else:
            if form['inv_state'] != 'all':
                where_str = ''' WHERE inv.state = '%s' AND inv.type = 'out_invoice'  '''%form['inv_state']
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



