# coding: utf-8
from odoo import models, fields, api, _


class AccountAccount(models.Model):
    _inherit = "account.account"

    recasting_account = fields.Boolean(
        "Account to recasting exercise", default=False
    )

    @api.onchange("recasting_account")
    def _onchange_recasting_account(self):
        for rec in self:
            acc_obj = self.search([("recasting_account", "=", True)])
            if rec.recasting_account:
                if acc_obj:
                    error_string = (
                        _(
                            "Already exist another recasting account (%r)."
                        )
                        % acc_obj.name
                    )
                    rec.recasting_account = False
                    self.env.user.notify_warning(error_string, "Error")
