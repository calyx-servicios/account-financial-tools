from odoo import models, api


class GeneralLedgerReportCompute(models.TransientModel):
    """Here, we just define methods.
    For class fields, go more top at this file.
    """

    _inherit = "report_general_ledger"

    @api.multi
    def compute_data_for_report(
        self, with_line_details=True, with_partners=True
    ):
        self.ensure_one()
        # Compute report data
        self._inject_account_values()

        if with_partners:
            self._inject_partner_values()
            if not self.filter_partner_ids:
                self._inject_partner_values(only_empty_partner=True)

        # NOTE
        # This function was deprecated
        # The function now is in /wizard/fiscal_year_closing.py

        # Add unaffected earnings account
        # if (not self.filter_account_ids or
        #         self.unaffected_earnings_account.id in
        #         self.filter_account_ids.ids):
        #     self._inject_unaffected_earnings_account_values()

        # Call this function even if we don't want line details because,
        # we need to compute
        # at least the values for unaffected earnings account
        # In this case, only unaffected earnings account values are computed
        only_unaffected_earnings_account = not with_line_details
        self._inject_line_not_centralized_values(
            only_unaffected_earnings_account=only_unaffected_earnings_account
        )

        if with_line_details:
            self._inject_line_not_centralized_values(
                is_account_line=False, is_partner_line=True
            )

            self._inject_line_not_centralized_values(
                is_account_line=False,
                is_partner_line=True,
                only_empty_partner_line=True,
            )

            if self.centralize:
                self._inject_line_centralized_values()

        if self.show_analytic_tags:
            # Compute analytic tags
            self._compute_analytic_tags()

        # Refresh cache because all data are computed with SQL requests
        self.invalidate_cache()
