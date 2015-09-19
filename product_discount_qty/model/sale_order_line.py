# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.addons.account_bank_statement_extensions.wizard.confirm_statement_line import confirm_statement_line

from openerp.osv import fields, osv
from openerp.tools.translate import _

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False, context=None):

        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)

        if not product or not uos:
            return result
        if context.get('saleman', False):
            partner_obj = self.pool.get('res.partner')
            user_obj = self.pool.get('res.users')
            uom_obj = self.pool.get('product.uom')
            conf_obj = self.pool.get('product.discount.qty')

            partner_brw = partner_obj.browse(cr, uid, partner_id)
            user_br = user_obj.browse(cr, uid, context['saleman'])
            if not user_br.partner_id:
                return result

            uos_obj = uom_obj.browse(cr, uid, uos)
            full_qty_uos = qty_uos * uos_obj.factor
            dis_kg = 0

            config_ids = conf_obj.search(cr, uid, [('user_ids', '=', user_br.id)])
            sql= '''
                            SELECT temp.qty, temp.disc_qty
                            FROM (SELECT disc.qty, disc.disc_qty
                                     FROM product_discount_qty disc
                                     INNER JOIN discount_qty_user_rel user_rel on (user_rel.disc_id=disc.id)
                                     LEFT JOIN discount_qty_partner_rel part_rel on (part_rel.disc_id=disc.id)
                                     LEFT JOIN discount_qty_product_rel disc_rel on (disc_rel.disc_id=disc.id)
                                     WHERE user_rel.user_id = %s AND disc.qty <= %s AND disc.determine = 'saleman'
                                     AND (part_rel.partner_id = %s or part_rel.partner_id is null)
                                     AND (disc_rel.product_id = %s or disc_rel.product_id is null)
                                     ORDER BY disc.qty DESC ) as temp ORDER BY temp.disc_qty DESC LIMIT 1
            '''
            sql1 =sql%(user_br.id, full_qty_uos, partner_id, product)
            cr.execute(sql1)
            datas = cr.dictfetchone()
            if datas:
                #viet theo lay user local marhet
                while (datas and datas['qty']):
                    full_qty_uos -= datas['qty']
                    dis_kg += datas['disc_qty']
                    sql1 =sql%(user_br.id, full_qty_uos, partner_id, product)
                    cr.execute(sql1)
                    datas = cr.dictfetchone()
            else:
                sql= '''
                            SELECT temp.qty, temp.disc_qty
                            FROM (SELECT disc.qty, disc.disc_qty
                                     FROM product_discount_qty disc
                                     LEFT JOIN discount_qty_user_rel user_rel on (user_rel.disc_id=disc.id)
                                     LEFT JOIN discount_qty_partner_rel part_rel on (part_rel.disc_id=disc.id)
                                     LEFT JOIN discount_qty_product_rel disc_rel on (disc_rel.disc_id=disc.id)
                                     WHERE user_rel.user_id is null AND disc.determine = 'saleman' AND disc.qty <= %s
                                     AND (part_rel.partner_id = %s or part_rel.partner_id is null)
                                     AND (disc_rel.product_id = %s or disc_rel.product_id is null)
                                     ORDER BY disc.qty DESC ) as temp ORDER BY temp.disc_qty DESC LIMIT 1
                '''
                sql1 =sql%(full_qty_uos, partner_id, product)
                cr.execute(sql1)
                datas = cr.dictfetchone()
                if datas:
                     #viet theo lay user other market
                    while (datas and datas['qty']):
                        full_qty_uos -= datas['qty']
                        dis_kg += datas['disc_qty']
                        sql1 =sql%(full_qty_uos, partner_id, product)
                        cr.execute(sql1)
                        datas = cr.dictfetchone()
                else:
                    same_market = 'other'
                    for categ in user_br.partner_id.category_id:
                        if categ in partner_brw.category_id:
                            same_market = 'local'
                            break



                    sql= '''
                            SELECT temp.qty, temp.disc_qty
                            FROM (SELECT disc.qty, disc.disc_qty
                                     FROM product_discount_qty disc
                                     LEFT JOIN discount_qty_partner_rel part_rel on (part_rel.disc_id=disc.id)
                                     LEFT JOIN discount_qty_product_rel disc_rel on (disc_rel.disc_id=disc.id)
                                     WHERE disc.type = '%s' AND disc.qty <= %s  AND disc.determine = 'tag'
                                     AND (part_rel.partner_id = %s or part_rel.partner_id is null)
                                     AND (disc_rel.product_id = %s or disc_rel.product_id is null)
                                     ORDER BY disc.qty DESC ) as temp ORDER BY temp.disc_qty DESC LIMIT 1
                    '''
                    sql1 =sql%(same_market, full_qty_uos, partner_id, product)
                    cr.execute(sql1)
                    datas = cr.dictfetchone()

                    while (datas and datas['qty']):
                        full_qty_uos -= datas['qty']
                        dis_kg += datas['disc_qty']
                        sql1 =sql%(same_market, full_qty_uos, partner_id, product)
                        cr.execute(sql1)
                        datas = cr.dictfetchone()
            result['value'].update({'discount_kg': dis_kg})
        return result
