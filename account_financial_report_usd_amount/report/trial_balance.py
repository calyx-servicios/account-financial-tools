# Copyright 2020 Calyx Servicios S.A.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class TrialBalanceReportCompute(models.TransientModel):
    _inherit = "report_trial_balance"

    usd_amount = fields.Boolean(string="USD Amount", default=False)

    exchange_rate_amount = fields.Float(
        string="Exchange Rate", default=0.0
    )

    def _prepare_report_general_ledger(self, account_ids):
        self.ensure_one()
        res = super(
            TrialBalanceReportCompute, self
        )._prepare_report_general_ledger(account_ids)
        if self.usd_amount:
            res.update(
                {
                    "usd_amount": self.usd_amount,
                    "exchange_rate_amount": self.exchange_rate_amount,
                }
            )
        return res
