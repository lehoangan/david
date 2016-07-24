# -*- coding: utf-8 -*-

from openerp.addons.account.report.account_general_ledger \
    import general_ledger
from openerp.osv import osv

class general_ledger_fix(general_ledger):

    def _get_account(self, data):
        if data['model'] == 'account.account' and data['ids']:
            return self.pool.get('account.account').browse(self.cr, self.uid, data['ids'][0]).company_id.name
        return super(general_ledger, self)._get_account(data)

class report_generalledger(osv.AbstractModel):
    _name = 'report.account.report_generalledger'
    _inherit = 'report.abstract_report'
    _template = 'account.report_generalledger'
    _wrapped_report_class = general_ledger_fix