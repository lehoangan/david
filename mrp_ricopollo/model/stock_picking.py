# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
from openerp.tools.translate import _
import time

class stock_picking(osv.osv):
   
    _inherit = "stock.picking"    
    _columns = {
        'mrp_id': fields.many2one('mrp.production', 'MO', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
    }
    
    def action_revert_done(self, cr, uid, ids, context=None):
        if not len(ids):
            return False

        from openerp import netsvc
        for picking in self.browse(cr, uid, ids, context):
            for line in picking.move_lines:
                line.write({'state': 'draft'})
            self.write(cr, uid, [picking.id], {'state': 'draft'})
            wf_service = netsvc.LocalService("workflow")
            # Deleting the existing instance of workflow
            wf_service.trg_delete(uid, 'stock.picking', picking.id, cr)
            wf_service.trg_create(uid, 'stock.picking', picking.id, cr)
        for (id,name) in self.name_get(cr, uid, ids):
            message = _("The stock picking '%s' has been set in draft state.") %(name,)
            self.log(cr, uid, id, message)
        return True

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
            product_name = product_obj.default_code and '[%s]%s'%(product_obj.default_code, product_obj.name) or product_obj.name
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
        stk_move_ids = context.get('stock_move_ids', [])
        if stk_move_ids:
            return self.get_finish_price(cr, uid, prod_id, date, account_id, context)

        sql = '''
            SELECT coalesce(SUM(debit-credit),0) as amount, coalesce(SUM(CASE
                                                      WHEN debit > 0 THEN quantity
                                                      ELSE -quantity
                                                    END),0) as qty
                    FROM account_move_line
                    WHERE account_id = %s AND date <= '%s' AND product_id = %s AND (closed_cycle is null OR closed_cycle = FALSE)
        '''%(account_id, date, prod_id)
        cr.execute(sql)
        data = cr.dictfetchone()
        price = data['qty'] and data['amount']/data['qty'] or 0
        return price

    def get_finish_price(self, cr, uid, prod_id, date, account_id, context={}):

        date = date[:10]
        stk_move_ids = context.get('stock_move_ids', [])
        old_stock_move_ids = context.get('old_stock_move_ids', [])
        remain_qty = context.get('remain_qty', [])
        move_condition = ' AND stock_move_id in %s '%str(tuple(stk_move_ids+[-1,-1]))
        old_move_condition = ' AND stock_move_id in %s '%str(tuple(old_stock_move_ids+[-1,-1]))
        sql = '''
                SELECT coalesce(SUM(debit-credit),0) as amount
                        FROM account_move_line
                        WHERE account_id = %s AND date <= '%s' %s AND (closed_cycle is null OR closed_cycle = FALSE)
                '''%(account_id, date, move_condition)
        cr.execute(sql)
        data = cr.dictfetchone()
        amount = data['amount']#material fee
        sql = '''
                SELECT coalesce(SUM(debit-credit),0) as amount
                        FROM account_move_line
                        WHERE account_id = %s AND date <= '%s' %s AND product_id = %s AND (closed_cycle is null OR closed_cycle = FALSE)
                '''%(account_id, date, old_move_condition, prod_id)
        cr.execute(sql)
        data = cr.dictfetchone()
        amount += data['amount']#deduct fee transferred to finished goods
        price = remain_qty and amount/remain_qty or 0
        return price

    def make_cost_price_journal_entry(self, cr, uid, ids, context=None):
        warehouse = self.pool.get('stock.warehouse')
        for pick in self.browse(cr, uid, ids, context):
            move_lines = []
            stock_move_data = ''
            journal_id = False
            period_ids = self.pool.get('account.period').find(cr, uid, pick.date_done)
            if not period_ids:
                raise osv.except_osv('Invalid Action', 'You havent defined period for date: %s'%pick.date_done)

            for move in pick.move_lines:
                if move.state != 'done' or move.location_dest_id == move.location_id:
                    continue
                warehouse_ids = warehouse.search(cr, uid, [('lot_stock_id','=', move.location_id.id),
                                                                              # ('is_farm', '=', True),
                                                                              # ('state', '=', 'open')
                                                           ])

                if not warehouse_ids:
                    warehouse_ids = warehouse.search(cr, uid, [('lot_stock_id','=', move.location_dest_id.id),
                                                                              # ('is_farm', '=', True),
                                                                              # ('state', '=', 'open')
                                                               ])
                    if not warehouse_ids: # and not pick.mrp_id:
                        continue

                # elif not pick.mrp_id:
                #     continue

                warehouse_obj = warehouse.browse(cr, uid, warehouse_ids[0])
                if not journal_id and warehouse_obj.journal_id:
                    journal_id = warehouse_obj.journal_id.id
                elif not journal_id:
                    journal_id = move.product_id.categ_id.property_stock_journal and \
                                                    move.product_id.categ_id.property_stock_journal.id or False
                account_credit, account_debit = self.get_account(cr, uid, move, context)
                cost_price = self.get_cost_price(cr, uid, move.product_id.id, move.date, account_credit, context)
                if not cost_price:
                    cost_price = self.get_latest_purchase_price(cr, uid, move.product_id.id, move.date, move.product_uom)
                if not cost_price: continue
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
                move_id = self.create_account_move(cr, uid, journal_id, pick.origin and '%s:%s'%(pick.name,pick.origin or '') or pick.name, \
                                                   period_obj, pick.date_done, move_lines, \
                                                   dict(context, note_picking=pick.note))
                self.pool.get('account.move').button_validate(cr, uid, [move_id], context)
            stock_move_data and cr.execute(stock_move_data)
        return True

    def _create_backorder(self, cr, uid, picking, backorder_moves=[], context=None):
        res = super(stock_picking, self)._create_backorder(cr, uid, picking, backorder_moves, context)
        if picking.state == 'done':
            self.make_cost_price_journal_entry(cr, uid, [picking.id], context)
            if picking.mrp_id and picking.mrp_id.state not in ('draft', 'cancel', 'done'):
                for move in picking.move_lines:
                    if not move.raw_material_production_id:
                        move.write({'raw_material_production_id': picking.mrp_id.id})
        return res
