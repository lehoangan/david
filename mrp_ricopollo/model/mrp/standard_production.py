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
import time

class standard_production(osv.osv):
    _name = 'standard.production'
    _inherit = ['mail.thread']

    _columns ={        
        'type': fields.selection([('Male', 'Macho'), ('female', 'Hembra'), ('mixed', 'Mixto')], 'Type', required=True),
        'date': fields.integer('Day'),
        'chicken_weight': fields.integer('Chicken Weight (gr)'),
        'daily_weight': fields.integer('Daily Weight Gain (gr)'),
        'average_weight': fields.float('Average weight gain per week (gr)', digits=(12,2)),
        'food_consumption': fields.integer('Daily food consumption per chicken (gr)'),
        'acumulated_consumption': fields.integer('Acumulated Consumption (gr)'),
        'rate': fields.float('Food Convertion Rate', digits=(12,3)),
    }
