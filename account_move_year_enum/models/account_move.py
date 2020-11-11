# coding: utf-8
import logging

from odoo import models, fields, api, _
from odoo.exceptions import MissingError


class AccountMove(models.Model):
    _inherit = "account.move"

    fiscal_year = fields.Many2one(
        comodel_name='account.fiscal.year',
        string='Fiscal Year',
        ondelete='restrict',
        default=lambda self: False)

    numeration = fields.Integer(
        string='Account Move Number'
    )

    @api.multi
    def post(self):
        year_to_assign = self.env['account.fiscal.year'].search([
          ('date_from', '<=', self.date),
          ('date_to', '>=', self.date),
          ('company_id', '=', self.env.user.company_id.id)
        ], limit=1)

        if year_to_assign:
            self.fiscal_year = year_to_assign.id
            account_moves_last_enum = self.env['account.move'].search([
                ('date', '>=', year_to_assign.date_from),
                ('date', '<=', year_to_assign.date_to),
                ('state', '=', 'posted'),
                ('company_id', '=', self.env.user.company_id.id),
                ('numeration', '!=', 0)
            ], order='numeration desc', limit=1)

            if not account_moves_last_enum.numeration:
                self.numeration = 1
            else:
                self.numeration = account_moves_last_enum.numeration + 1
        else:
            raise MissingError(_('You have to create a Fiscal Year to assign %s year to an account '
                                 'move.\nGo To Configuration > Accounting > Fiscal Years') % self.date[:4])

        return super().post()

    @api.multi
    def button_cancel(self):
        self.write({'numeration': 0})
        return super().button_cancel()

