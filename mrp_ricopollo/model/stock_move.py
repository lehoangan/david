# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
from openerp.tools.translate import _

class stock_move(osv.osv):
    _inherit = "stock.move"
    _columns = {
        'account_debit_id': fields.many2one('account.account', 'Account Debit', ondelete="cascade", domain=[('type','<>','view'), ('type', '<>', 'closed')], select=2),
        'account_credit_id': fields.many2one('account.account', 'Account Crebit', ondelete="cascade", domain=[('type','<>','view'), ('type', '<>', 'closed')], select=2),
        'cost_price': fields.float('Cost Price' , digits=(16,6)),
        'dead_chicken': fields.boolean('Dead Chicken'),
    }
stock_move()
    
