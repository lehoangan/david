# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
from openerp.tools.translate import _

class stock_picking(osv.osv):
   
    _inherit = "stock.picking"    
    _columns = {

    }

    def get_account(self, cr, uid, move, context={}):
        account_debit_id, account_credit_id = False, False
        if move.location_dest_id.account_id:
            account_debit_id = move.location_dest_id.account_id.id
        if move.location_id.account_id:
            account_credit_id = move.location_id.account_id.id
        else:
            if move.product_id.property_account_expense:
                account_credit_id = move.product_id.property_account_expense.id
            elif move.product_id.categ_id.property_account_cost_price_categ:
                account_credit_id = move.product_id.categ_id.property_account_cost_price_categ.id
        if not account_credit_id:
            raise osv.except_osv(_(u'Error!'),
                                _(u' Not config account on source location!'))
        if not account_debit_id:
            raise osv.except_osv(_(u'Error!'),
                                _(u' Not config account on dest location!'))
        return account_credit_id, account_debit_id

    def create_account_move(self, cr, uid, journal_id, name, period_obj, date, lst_accout_move_line, context):
        import time
        move_pool = self.pool.get('account.move')
        journal_description = context.get('description', '')
        journal_description = journal_description and journal_description + ' ' + name or name
        move = {
                'ref': journal_description,
                'name': journal_description,
                'journal_id': journal_id,
                'date': date or time.strftime('%Y-%m-%d'),
                'period_id': period_obj.id,
                'line_id': lst_accout_move_line,
                'narration': context.get('note_picking', name),
            }
        move_id = move_pool.create(cr, uid, move, context=context)
        return move_id

    def _prepare_account_move_line(self, cr, uid, journal_id, product_obj,quantity, uom_id, \
                                                   amount_cost_price, period_id, \
                                                   account_debit, account_credit, \
                                                   stock_move_id, date, context):

        name = context.get('name', '')
        result =[]
        if account_credit and account_debit:
            # move line credit
            debit1 = 0
            credit1 = round(amount_cost_price*(quantity or 1),0)
            product_name = '[%s]%s'%(product_obj.default_code, product_obj.name)
            name = name and '%s: %s'%(name, product_name) or product_name
            move_line1 = {
                'name'                  : name,
                'debit'                 : debit1,
                'credit'                : credit1,
                'account_id'            : account_credit,
                'journal_id'            : journal_id,
                'period_id'             : period_id,
                'product_id'            : product_obj.id,
                'quantity'              : quantity,
                'product_uom_id'        : uom_id,
                'currency_id'           : False,
                'date'                  : date,
                'stock_move_id'         : stock_move_id,
            }
            result.append((0, 0, move_line1))

            #account move line debit
            debit2 = round(amount_cost_price*(quantity or 1),0)
            credit2= 0
            move_line2 = {
                'name'                  : name,
                'debit'                 : debit2,
                'credit'                : credit2,
                'account_id'            : account_debit,
                'journal_id'            : journal_id,
                'period_id'             : period_id,
                'product_id'            : product_obj.id,
                'quantity'              : quantity,
                'product_uom_id'        : uom_id,
                'currency_id'           : False,
                'date'                  : date,
                'stock_move_id'         : stock_move_id,
            }
            result.append((0, 0, move_line2))
        return result

    def get_latest_purchase_price(self,cr, uid, prod_id, date, uom_obj):
        price = 0
        purchase_obj = self.pool.get('purchase.order.line')
        ids = purchase_obj.search(cr, uid, [('product_id','=',prod_id),('price_unit','>',0), ('date_planned','<=', date)], order = "date_planned desc, id desc", limit=1)
        if ids:
            line_obj = purchase_obj.browse(cr, uid, ids[0])
            price = line_obj.price_unit / line_obj.product_uom.factor * uom_obj.factor
            if line_obj.order_id.pricelist_id.currency_id and line_obj.order_id.pricelist_id.currency_id != line_obj.company_id.currency_id:
                price = self.pool.get('res.currency').compute(cr, uid, line_obj.order_id.pricelist_id.currency_id.id, line_obj.company_id.currency_id.id, price, {'date': line_obj.date_planned})
        else:
            price = self.pool.get('product.product').browse(cr, uid, prod_id).standard_price
        return price

    def get_cost_price(self, cr, uid, prod_id, date, account_id, context={}):

        date = date[:10]
        sql = '''
            SELECT coalesce(SUM(debit-credit),0) as amount, coalesce(SUM(CASE
                                                      WHEN debit > 0 THEN quantity
                                                      ELSE -quantity
                                                    END),0) as qty
                    FROM account_move_line
                    WHERE account_id = %s AND product_id = %s AND date <= '%s'
        '''%(account_id, prod_id, date)
        cr.execute(sql)
        data = cr.dictfetchone()
        price = data['qty'] and data['amount']/data['qty'] or 0
        return price

    def make_cost_price_journal_entry(self, cr, uid, ids, context=None):
        move_id = False
        for pick in self.browse(cr, uid, ids, context):
            move_lines = []
            journal_id = False
            period_ids = self.pool.get('account.period').find(cr, uid, pick.date_done)
            if not period_ids:
                raise osv.except_osv('Invalid Action', 'You havent defined period for date: %s'%move.date_done)
            stock_move_data = ''
            for move in pick.move_lines:
                if move.state != 'done':
                    continue
                if not journal_id:
                    journal_id = move.product_id.categ_id.property_stock_journal and \
                                                    move.product_id.categ_id.property_stock_journal.id or False
                account_credit, account_debit = self.get_account(cr, uid, move, context)
                cost_price = self.get_cost_price(cr, uid, move.product_id.id, move.date, account_credit, context)
                line = self._prepare_account_move_line(cr, uid, journal_id, move.product_id, \
                                                           move.product_qty, move.product_uom.id, \
                                                           cost_price, period_ids[0], \
                                                           account_debit, account_credit, move.id, move.date, \
                                                           dict(context, name = 'Transfer expense from %s to %s'%(move.location_id.name, move.location_dest_id.name)))
                move_lines += line
                stock_move_data += ''' Update stock_move set cost_price=%s,
                                                             account_debit_id=%s,
                                                             account_credit_id=%s where id =%s ;
                                    '''%(cost_price, account_debit, account_credit, move.id)
            if move_lines:
                period_obj = self.pool.get('account.period').browse(cr, uid, period_ids[0])
                move_id = self.create_account_move(cr, uid, journal_id, '%s:%s'%(pick.name,pick.origin), \
                                                   period_obj, pick.date_done, move_lines, \
                                                   dict(context, note_picking=pick.note))
                self.pool.get('account.move').button_validate(cr, uid, [move_id], context)
            stock_move_data and cr.execute(stock_move_data)
        return True
