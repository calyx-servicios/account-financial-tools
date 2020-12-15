# Copyright 2020 Calyx Servicios S.A.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api


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

    @api.multi
    def compute_data_for_report(self):
        super(TrialBalanceReportCompute, self).compute_data_for_report()
        if self.usd_amount:
            self._calculate_acc_diff()

    def _calculate_acc_diff(self):
        """
        With the amounts in USD the sum of balances is != 0.0,
        this function extends the compute_data to aggregate another account
        with the difference in amount (debit or credit)
        to close de balance at 0.0.
        """
        final_balance_total = 0
        rtba_obj = self.env["report_trial_balance_account"]
        acc_diff_exchange = self.env.ref(
            "account_financial_report_usd_amount.account_diff_exchange_rate"
        )

        for line in rtba_obj.search([("report_id", "=", self.id)]):
            if line.final_balance == 0.0:
                continue
            else:
                final_balance_total += line.final_balance
                continue

        debit = (
            final_balance_total if final_balance_total < 0.0 else 0.0
        )
        credit = (
            final_balance_total if final_balance_total > 0.0 else 0.0
        )
        if debit or credit != 0.0:
            debit_sign = debit * (-1) if debit < 0.0 else debit
            rtba_params = (
                0.0,
                debit_sign,
                credit,
                (debit_sign - credit),
                (debit_sign - credit),
                self.id,
                acc_diff_exchange.id,
            )

            rtba_query = """
            UPDATE report_trial_balance_account
            SET
            initial_balance = %s,
            debit = %s,
            credit = %s,
            period_balance = %s,
            final_balance = %s
            WHERE report_id = %s AND account_id = %s
            """
            self.env.cr.execute(rtba_query, rtba_params)
