# Copyright 2020 Calyx Servicios S.A.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api


class GeneralLedgerReport(models.TransientModel):
    _inherit = "report_general_ledger"

    usd_amount = fields.Boolean(string="USD Amount", default=False)

    exchange_rate_amount = fields.Float(
        string="Exchange Rate", default=0.0
    )

    @api.multi
    def compute_data_for_report(
        self, with_line_details=True, with_partners=True
    ):
        super(GeneralLedgerReport, self).compute_data_for_report(
            with_line_details=True, with_partners=True
        )
        if self.usd_amount:
            if self.exchange_rate_amount > 0.0:
                self._compute_amount_balance_usd()
            self._compute_extra_initial_balance_usd()

    def _compute_amount_balance_usd(self):
        rgla = self.env["report_general_ledger_account"]
        exch_rate = self.exchange_rate_amount
        for acc in rgla.search([("report_id", "=", self.id)]):
            acc.initial_debit = acc.initial_debit / exch_rate
            acc.final_debit = acc.final_debit / exch_rate
            acc.initial_credit = acc.initial_credit / exch_rate
            acc.final_credit = acc.final_credit / exch_rate
            acc.initial_balance = acc.initial_balance / exch_rate
            acc.final_balance = acc.final_balance / exch_rate

    def _compute_extra_initial_balance_usd(self):
        rgla = self.env["report_general_ledger_account"]
        for acc in rgla.search([("report_id", "=", self.id)]):
            query_update_account_params = (acc.account_id.id,)
            rtbi_query = """
            SELECT amount FROM report_trial_balance_initial_amount 
            rtb WHERE rtb.account_id = %s AND rtb.state = 'done'
            """
            self.env.cr.execute(rtbi_query, query_update_account_params)
            rtbi = self.env.cr.fetchone()
            if rtbi:
                extra_initial_balance = rtbi[0]
                acc.initial_balance += extra_initial_balance
                acc.final_balance += extra_initial_balance
