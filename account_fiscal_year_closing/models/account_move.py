# coding: utf-8
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    fy_closing_acc_move = fields.Boolean(
        "Fiscal Year Closing Move", default=False
    )

    fy_opening_acc_move = fields.Boolean(
        "Fiscal Year Opening Move", default=False
    )

    recasting_acc_move = fields.Boolean("Recasting Move", default=False)
    consolidation_acc_move = fields.Boolean(
        "Consolidation Results Move", default=False
    )
    closing_equity_move = fields.Boolean(
        "Equity Closing Move", default=False
    )

    @api.model
    def create(self, vals):
        date = vals.get("date")
        fiscal_year, error_string = self._get_current_fy(date)
        if fiscal_year:
            raise ValidationError(error_string)
        return super(AccountMove, self).create(vals)

    @api.multi
    def write(self, vals):
        date = vals.get("date")
        fiscal_year, error_string = self._get_current_fy(date)
        if fiscal_year:
            raise ValidationError(error_string)
        return super(AccountMove, self).write(vals)

    def _get_current_fy(self, date):
        fiscal_year = self.env["account.fiscal.year"].search(
            [
                ("date_from", "<=", date),
                ("date_to", ">=", date),
                ("company_id", "=", self.env.user.company_id.id),
                ("fiscal_year_close", "=", True),
            ],
            limit=1,
        )

        error_string = _(
            "You cannot create a move in closed period. \
            \nYou first have to revert the closing process for this \
             fiscal year."
        )
        return fiscal_year, error_string
