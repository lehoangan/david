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

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time

class final_part_of_product(osv.osv):
    _name = 'final.part.of.product'
    _inherit = ['mail.thread']
    _columns ={
        'slaughtery_id': fields.many2one('slaughtery.chickens.daily', 'Número de Boleta', required=True,
        readonly=True, states={'draft': [('readonly', False)]}),
        'date': fields.date('Date', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'name': fields.char('Nro. Recibo', 100, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'warehouse_id': fields.many2one('stock.warehouse', 'Farm', required=True, domain=[('is_farm', '=', True)],
        readonly=True, states={'draft': [('readonly', False)]}),
        'warehouse_to_id': fields.many2one('stock.warehouse', 'Move To', required=True,
        readonly=True, states={'draft': [('readonly', False)]}),
        'cycle_id': fields.many2one('history.cycle.form', 'Cycle', domain="[('warehouse_id','=', warehouse_id),('date_end', '=', False)]",
        readonly=True, states={'draft': [('readonly', False)]}),

        'line_used_ids': fields.one2many('final.part.of.product.used.detail', 'parent_used_id', 'Used Details',
        readonly=True, states={'draft': [('readonly', False)]}),

        'line_finish_ids': fields.one2many('final.part.of.product.finish.detail', 'parent_finish_id', 'Finish Details',
        readonly=True, states={'draft': [('readonly', False)]}),
        'picking_id': fields.many2one('stock.picking', 'Picking'),

        'note': fields.text('Note'),
        'state': fields.selection([('draft', 'Draft'),
                                   ('confirm', 'Confirm'),
                                   ('cancel','Cancel')], 'State', readonly=True)
    }
    _order="date desc"

    def _get_warehouse_to_id(self, cr, uid, context=None):
        warehouse_obj = self.pool.get('stock.warehouse')
        warehouse_ids = warehouse_obj.search(cr, uid, [('code', '=', 'MAT2-FRIG')])
        return warehouse_ids and warehouse_ids[0] or False

    _defaults = {
        'date': lambda*a: time.strftime('%Y-%m-%d'),
        'state': 'draft',
        'warehouse_to_id': _get_warehouse_to_id,
     }

    def onchange_slaughtery_id(self, cr, uid, ids, slaughtery_id, context={}):
        if not slaughtery_id:
            return {'value': {}}

        slaughtery = self.pool.get('slaughtery.chickens.daily').browse(cr, uid, slaughtery_id, context)

        return {'value': {
            'warehouse_id': slaughtery.to_warehouse_id and slaughtery.to_warehouse_id.id or False,
            # 'cycle_id': slaughtery.cycle_id.id,
            'date': slaughtery.date,
            'name': slaughtery.name,
        }}

    def action_approve(self, cr, uid, ids, context=None):

        stock_picking = self.pool.get('stock.picking')
        stock_warehouse = self.pool.get('stock.warehouse')
        stock_move_obj = self.pool.get('stock.move')
        obj = self.browse(cr, uid, ids, context)[0]
        warehouse = obj.warehouse_to_id
        int_type_id = warehouse.int_type_id and warehouse.int_type_id.id or False
        location_dest_id = warehouse.lot_stock_id.id

        picking_id = stock_picking.create(cr, uid, {
                                                    'origin': 'Pollo Trozado: %s'%obj.name,
                                                    'move_type': 'direct',
                                                    'picking_type_id': int_type_id,
                                                }, context=context)
        move_ids = []
        for line in obj.line_finish_ids:
            stock_move = {
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.weight,
                'location_id': obj.warehouse_id.lot_stock_id.id,
                'location_dest_id': location_dest_id,
                'picking_id': picking_id,
                'product_uom': line.product_id.uom_id.id,
                # 'qty_kg': line.weight,
            }
            move_id = stock_move_obj.create(cr, uid, stock_move, context)
            move_ids += [move_id]

        stock_move_obj.action_assign(cr, uid, move_ids, context=context)
        stock_picking.action_done(cr, uid, [picking_id], context)
        self.write(cr, uid, ids, {'state': 'confirm', 'picking_id': picking_id}, context)
        return self.make_cost_price_journal_entry(cr, uid, ids, context)

    def get_cost_price(self, cr, uid, obj, context=None):
        cost_price = 0
        move_ids = []

        for move in obj.slaughtery_id.picking_id.move_lines:
            move_ids += [move.id]
        aml_obj = self.pool.get('account.move.line')
        aml_ids = aml_obj.search(cr, uid, [('stock_move_id', 'in', move_ids),
                                           ('debit', '>', 0)])
        total = 0
        for move in aml_obj.browse(cr, uid, aml_ids):
            total += move.debit
        return total

    def _prepare_account_move_line(self, cr, uid, journal_id, product_obj,quantity, uom_id, \
                                                   amount_cost_price, period_id, \
                                                   account_debit, account_credit, \
                                                   stock_move_id, date, context):

        name = context.get('name', '')
        result =[]
        if account_credit and account_debit:
            # move line credit
            debit1 = 0
            credit1 = round(amount_cost_price, 0)
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
            debit2 = round(amount_cost_price, 0)
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

    def make_cost_price_journal_entry(self, cr, uid, ids, context=None):
        warehouse = self.pool.get('stock.warehouse')
        for obj in self.browse(cr, uid, ids, context):

            pick = obj.picking_id
            move_lines = []
            stock_move_data = ''
            journal_id = False

            period_ids = self.pool.get('account.period').find(cr, uid, pick.date_done)
            if not period_ids:
                raise osv.except_osv('Invalid Action', 'You havent defined period for date: %s'%pick.date_done)
            warehouse_obj = obj.warehouse_to_id
            account_credit = obj.warehouse_id.account_id and obj.warehouse_id.account_id.id or ''
            account_debit = obj.warehouse_to_id.account_id and obj.warehouse_to_id.account_id.id or ''
            if not account_credit:
                raise osv.except_osv(_(u'Error!'),
                                    _(u' Not config account on source location!'))
            if not account_debit:
                raise osv.except_osv(_(u'Error!'),
                                    _(u' Not config account on dest location!'))

            total_kg = sum([move.product_uom_qty for move in pick.move_lines])
            total_amount = self.get_cost_price(cr, uid, obj, context)

            for move in pick.move_lines:
                if not journal_id and warehouse_obj.journal_id:
                    journal_id = warehouse_obj.journal_id.id
                elif not journal_id:
                    journal_id = move.product_id.categ_id.property_stock_journal and \
                                                    move.product_id.categ_id.property_stock_journal.id or False

                cost_price = total_kg and total_amount * (move.product_uom_qty/total_kg) or 0
                if not cost_price: continue
                line = self._prepare_account_move_line(cr, uid, journal_id, move.product_id, \
                                                           move.product_uom_qty, move.product_uom.id, \
                                                           cost_price, period_ids[0], \
                                                           account_debit, account_credit, move.id, move.date, \
                                                           dict(context, name = 'Transfer expense from %s to %s'%(move.location_id.name, move.location_dest_id.name)))
                move_lines += line
                stock_move_data += ''' Update stock_move set cost_price=%s,
                                                             account_debit_id=%s,
                                                             account_credit_id=%s where id =%s ;
                                    '''%(cost_price/move.product_uom_qty, account_debit, account_credit, move.id)
            if move_lines:
                period_obj = self.pool.get('account.period').browse(cr, uid, period_ids[0])
                move_id = self.pool.get('stock.picking').create_account_move(cr, uid, journal_id, pick.origin and '%s:%s'%(pick.name,pick.origin or '') or pick.name, \
                                                   period_obj, pick.date_done, move_lines, \
                                                   dict(context, note_picking=pick.note))
                self.pool.get('account.move').button_validate(cr, uid, [move_id], context)
            stock_move_data and cr.execute(stock_move_data)
        return True
    
    def action_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'})

    def action_set_to_draft(self, cr, uid, ids, context):
        return self.write(cr, uid, ids, {'state': 'draft'})

class final_part_of_product_used_detail(osv.osv):
    _name = 'final.part.of.product.used.detail'
    def _average_get(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res.update({obj.id: obj.weight/obj.qty })
        return res
    _columns={
        'product_id': fields.many2one('product.product', 'Productos', required=True),
        'parent_used_id': fields.many2one('final.part.of.product', 'Parent'),

        'qty': fields.float('Unit', required=True),
        'weight': fields.float('Weight', required=True),
        'average': fields.function(_average_get, string='Average weight', type='float'),
    }

    def onchange_qty(self, cr, uid, ids, qty, weight, context=None):
        if not qty or not weight:
            return {'value': {'average': 0}}

        return {'value': {'average': weight/qty}}


class final_part_of_product_finish_detail(osv.osv):
    _name = 'final.part.of.product.finish.detail'

    def _average_get(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res.update({obj.id: obj.weight/obj.qty })
        return res

    _columns={
        'product_id': fields.many2one('product.product', 'Productos', required=True),
        'parent_finish_id': fields.many2one('final.part.of.product', 'Parent'),

        'qty': fields.float('Unit', required=True),
        'weight': fields.float('Weight', required=True),
        'average': fields.function(_average_get, string='Average weight', type='float'),

    }

    def onchange_qty(self, cr, uid, ids, qty, weight, context=None):
        if not qty or not weight:
            return {'value': {'average': 0}}

        return {'value': {'average': weight/qty}}

 
