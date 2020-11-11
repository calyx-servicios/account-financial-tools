# coding: utf-8
from odoo import models, fields, api, _
from odoo.exceptions import MissingError


class AccountMoveWizard(models.TransientModel):
    _name = 'account.move.fiscal.year.report.wizard'

    fiscal_year = fields.Many2one('account.fiscal.year')

    by_period = fields.Boolean('Filter by period')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To', default=fields.Date.context_today)

    @api.multi
    def generate_xls_report(self):
        self.ensure_one()
        data = self.read()[0]
        report = self.env.ref(
            'account_move_year_enum.account_move_fy_report_action')
        return report.report_action(self, data=data)
