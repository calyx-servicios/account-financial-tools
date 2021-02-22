# Copyright 2020 Calyx Servicios S.A.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ReportTrialBalanceInitialAmount(models.Model):
    _name = "report.trial.balance.initial.amount"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Initial Balance"
    _rec_name = "account_name"

    _sql_constraints = [
        (
            "account_uniq",
            "unique(account_id)",
            "You only can have one record per account",
        ),
    ]

    READONLY_STATES = {
        "done": [("readonly", True)],
    }

    account_id = fields.Many2one(
        "account.account",
        string="Account",
        required=True,
        states=READONLY_STATES,
        track_visibility="always",
    )
    account_name = fields.Char("Account", related="account_id.name")

    account_type = fields.Many2one(
        "account.account.type", string="Account Type"
    )

    currency_id = fields.Many2one(
        "res.currency",
        "Currency",
        required=True,
        states=READONLY_STATES,
        default=lambda self: self.env.ref("base.USD").id,
    )

    state = fields.Selection(
        [("draft", "Draft"), ("done", "Validate")],
        string="Status",
        readonly=True,
        index=True,
        copy=False,
        default="draft",
        track_visibility="onchange",
    )

    amount = fields.Float(
        "Amount",
        required=True,
        states=READONLY_STATES,
        track_visibility="onchange",
    )

    date = fields.Date(
        "Date",
        required=True,
        states=READONLY_STATES,
        track_visibility="onchange",
    )

    @api.multi
    def cancel(self):
        if self.state == "done":
            self.state = "draft"

    @api.multi
    def validate(self):
        if self.state == "draft":
            self.state = "done"

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == "done":
                raise ValidationError(
                    _("You cannot delete a validate record!")
                )
        return super(ReportTrialBalanceInitialAmount, self).unlink()

    @api.onchange("account_id")
    def _onchange_account_id(self):
        for rec in self:
            if rec.account_id:
                rec.account_type = rec.account_id.user_type_id.id
            else:
                rec.account_type = False
