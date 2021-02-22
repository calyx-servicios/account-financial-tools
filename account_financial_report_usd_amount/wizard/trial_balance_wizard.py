# Copyright 2020 Calyx Servicios S.A.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, _
from odoo.exceptions import ValidationError


class TrialBalanceReportWizard(models.TransientModel):
    _inherit = "trial.balance.report.wizard"

    usd_amount = fields.Boolean(string="USD Amount", default=False)

    exchange_rate_amount = fields.Float(
        string="Exchange Rate", default=0.0
    )

    def _prepare_report_trial_balance(self):
        self.ensure_one()
        res = super(
            TrialBalanceReportWizard, self
        )._prepare_report_trial_balance()
        if self.usd_amount and self.exchange_rate_amount <= 0.0:
            raise ValidationError(
                _(
                    "The exchange rate amount it cannot be equal or less that 0.0"
                )
            )
        res.update(
            {
                "usd_amount": self.usd_amount,
                "exchange_rate_amount": self.exchange_rate_amount,
            }
        )

        return res
