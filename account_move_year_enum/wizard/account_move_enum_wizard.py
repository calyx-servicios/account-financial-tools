# coding: utf-8
from datetime import datetime
import logging
from odoo import models, fields, api


class AccountMoveEnumYearWizard(models.TransientModel):
    _name = 'account.move.enum.wizard'

    year_to_enum = fields.Many2one(
        comodel_name='account.fiscal.year',
        string='Fiscal Year To Enumerate',
        default=lambda self: False)

    @api.multi
    def enumerate_account_move_by_year(self):
        year = self.year_to_enum
        account_moves_to_enum = self.env['account.move'].search([
            ('date', '>=', year.date_from),
            ('date', '<=', year.date_to),
            ('state', '=', 'posted'),
            ('company_id', '=', self.env.user.company_id.id)
        ], order='date asc, create_date asc')

        num = 1
        for account_move in account_moves_to_enum:
            logging.info('Enumeration Account Move {} of {}'.format(num, len(account_moves_to_enum)))
            account_move.numeration = num
            account_move.fiscal_year = year
            num += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

