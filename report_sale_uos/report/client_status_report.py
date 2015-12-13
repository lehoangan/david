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
        self.total = 0
        self.localcontext.update({
            'get_customer': self.get_customer,
            'get_saleman': self.get_saleman,
            'get_market': self.get_market,
            'get_invoice': self.get_invoice,
            'get_total': self.get_total,
        })

    def get_total(self):
        return self.total

    def get_market(self, form):
        where = ''
        if form['market_ids']:
            where = 'WHERE categ.id in %s'%str(tuple(form['market_ids'] + [-1, -1]))
        select_str = """
                 SELECT
                        distinct (categ.id) as id,
                        categ.name
                FROM ( res_partner part
                       left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                       left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                ORDER BY categ.name
        """%where
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        for categ in res:
            if not categ['id']: continue
            result = self.pool.get('res.partner.category').name_get(self.cr, self.uid, categ['id'])
            if result and result[0]:
                categ['name'] = result[0][1]
        return res

    def get_saleman(self, form, market_id):
        where = ''
        if market_id:
            where = ' WHERE categ.id = %s'%market_id
        select_str = """
                 SELECT
                        distinct (ruser.id) as id,
                        part2.name
                FROM ( res_partner part
                       left join res_users ruser on (part.user_id=ruser.id)
                       left join res_partner part2 on (part2.id=ruser.partner_id)
                       left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                       left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                order by part2.name
        """%where
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        for tmp in res:
            amount = self.get_amount_customer(form, market_id, tmp['id'])
            tmp.update({'amount': amount})
        return res

    def get_amount_customer(self, form, market_id, user_id):
        where = ' WHERE 1=1 '
        if market_id:
            where += ' AND categ.id = %s'%market_id
        if user_id:
            where += ' AND part.user_id = %s'%user_id
        select_str = """
                 SELECT
                        distinct (part.id) as id,
                        part.name
                FROM ( res_partner part
                       left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                       left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                order by part.name
        """%where
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        partner= []
        partner_obj = self.pool.get('res.partner')
        amount = 0
        for part in res:
            partner.append(part['id'])
        part_ids = partner_obj.search(self.cr, self.uid, [('id', 'in', partner)])
        for part in partner_obj.browse(self.cr, self.uid, part_ids):
            amount += part.credit
        self.total += amount
        return amount

    def get_customer(self, form, market_id, user_id):
        where = ' WHERE 1=1 '
        if market_id:
            where += ' AND categ.id = %s'%market_id
        if user_id:
            where += ' AND part.user_id = %s'%user_id
        select_str = """
                 SELECT
                        distinct (part.id) as id,
                        part.name
                FROM ( res_partner part
                       left join res_partner_res_partner_category_rel rel on (rel.partner_id=part.id)
                       left join res_partner_category categ on (rel.category_id=categ.id))
                %s
                order by part.name
        """%where
        self.cr.execute(select_str)
        res = self.cr.dictfetchall()
        partner= []
        partner_obj = self.pool.get('res.partner')
        no = 0
        for part in res:
            partner.append(part['id'])
        part_ids = partner_obj.search(self.cr, self.uid, [('id', 'in', partner)])
        partner = []
        for part in partner_obj.browse(self.cr, self.uid, part_ids):
            no += 1
            partner.append({'no': no,
                            'part': part})
        return partner

    def get_invoice(self, partner_id):
        inv_ids = self.pool.get('account.invoice').search(self.cr, self.uid, [('partner_id', '=', partner_id), ('state', '=', 'open')])
        return len(inv_ids)



