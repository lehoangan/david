# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
from openerp.tools.translate import _

class product_template(osv.osv):
    _inherit = "product.template"
    _columns = {
        'food_type': fields.boolean('Food Type'),
    }

