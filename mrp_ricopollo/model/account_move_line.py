# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class account_move_line(osv.osv):
    _inherit = 'account.move.line'    
    _columns = { 
        'stock_move_id':fields.many2one('stock.move', 'Stock Move'),
        'closed_cycle': fields.boolean('Closed Cycle'),
        'quantity': fields.float('Quantity', digits_compute= dp.get_precision('Product Unit of Measure'), help="The optional quantity expressed by this line, eg: number of product sold. The quantity is not a legal requirement but is very useful for some reports."),
    }
    _defaults={
        'avg_computed': False,
    }

    def write(self, cr, uid, ids, datas, context=None, check=True, update_check=True):
        if datas.get('account_id', False):
            for obj in self.browse(cr, uid, ids, context):
                if obj.stock_move_id:
                    if obj.debit > 0:
                        obj.stock_move_id.write({'account_debit_id': datas['account_id']})
                    if obj.credit > 0:
                        obj.stock_move_id.write({'account_credit_id': datas['account_id']})
        return super(account_move_line, self).write(cr, uid, ids, datas, context=context, check=check, update_check=update_check)

    
