# Copyright 2020 Calyx Servicios S.A.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api


class GeneralLedgerReport(models.TransientModel):
    _inherit = "report_general_ledger"

    usd_amount = fields.Boolean(string="USD Amount", default=False)

    exchange_rate_amount = fields.Float(
        string="Exchange Rate", default=0.0
    )

    def _get_account_sub_subquery_sum_amounts(
        self, include_initial_balance, date_included
    ):
        """
        Return subquery used to compute sum amounts on accounts
        Group the amount by currency
        """

        if self.usd_amount:
            sub_subquery_sum_amounts = """
                SELECT
                    c.id AS currency_id,
                    a.id AS account_id,
                    SUM(
                        CASE 
                            WHEN ml.amount_currency = 0.0
                            THEN (ml.debit / %s)
                            WHEN ml.amount_currency > 0.0
                            THEN ml.amount_currency
                            ELSE 0
                        END
                        ) AS debit,
                    SUM(
                        CASE
                            WHEN ml.amount_currency = 0.0
                            THEN (ml.credit / %s)
                            WHEN ml.amount_currency < 0.0
                            THEN (ml.amount_currency * (-1))
                            ELSE 0
                        END
                        ) AS credit,
                    SUM(
                        CASE
                            WHEN ml.amount_currency = 0.0
                            THEN (ml.balance / %s )
                            WHEN ml.amount_currency != 0.0
                            THEN ml.amount_currency
                            ELSE 0
                        END
                        ) AS balance,
                    CASE
                        WHEN c.id IS NOT NULL
                        THEN SUM(ml.amount_currency)
                        ELSE NULL
                    END AS balance_currency
                FROM
                    accounts a
                INNER JOIN
                    account_account_type at ON a.user_type_id = at.id
                INNER JOIN
                    account_move_line ml
                        ON a.id = ml.account_id
            """
        else:
            sub_subquery_sum_amounts = """
                SELECT
                    a.id AS account_id,
                    SUM(ml.debit) AS debit,
                    SUM(ml.credit) AS credit,
                    SUM(ml.balance) AS balance,
                    c.id AS currency_id,
                    CASE
                        WHEN c.id IS NOT NULL
                        THEN SUM(ml.amount_currency)
                        ELSE NULL
                    END AS balance_currency
                FROM
                    accounts a
                INNER JOIN
                    account_account_type at ON a.user_type_id = at.id
                INNER JOIN
                    account_move_line ml
                        ON a.id = ml.account_id
            """

        if date_included:
            sub_subquery_sum_amounts += """
                AND ml.date <= %s
            """
        else:
            sub_subquery_sum_amounts += """
                AND ml.date < %s
            """

        if not include_initial_balance:
            sub_subquery_sum_amounts += """
                AND at.include_initial_balance != TRUE AND ml.date >= %s
            """
        else:
            sub_subquery_sum_amounts += """
                AND at.include_initial_balance = TRUE
            """

        if self.only_posted_moves:
            sub_subquery_sum_amounts += """
        INNER JOIN
            account_move m ON ml.move_id = m.id AND m.state = 'posted'
            """
        if self.filter_cost_center_ids:
            sub_subquery_sum_amounts += """
        INNER JOIN
            account_analytic_account aa
                ON
                    ml.analytic_account_id = aa.id
                    AND aa.id IN %s
            """
        if self.filter_analytic_tag_ids:
            sub_subquery_sum_amounts += """
        INNER JOIN
            move_lines_on_tags ON ml.id = move_lines_on_tags.ml_id
            """
        sub_subquery_sum_amounts += """
        LEFT JOIN
            res_currency c ON a.currency_id = c.id
        """
        sub_subquery_sum_amounts += """
        GROUP BY
            a.id, c.id
        """
        return sub_subquery_sum_amounts

    @api.multi
    def compute_data_for_report(
        self, with_line_details=True, with_partners=True
    ):
        super(GeneralLedgerReport, self).compute_data_for_report(
            with_line_details=True, with_partners=True
        )
        if self.usd_amount:
            self._compute_extra_initial_balance_usd()

    def _compute_extra_initial_balance_usd(self):
        """
        Update the initial balance of the accounts with the amounts in
        report_trial_balance_initial_amount
        """
        rgla = self.env["report_general_ledger_account"]
        date_init = self.date_from

        for acc in rgla.search([("report_id", "=", self.id)]):
            query_update_account_params = (
                acc.account_id.id,
                date_init,
            )
            rtbi_query = """
            SELECT amount FROM report_trial_balance_initial_amount 
            rtb WHERE rtb.account_id = %s AND rtb.state = 'done'
            AND date < %s
            """
            self.env.cr.execute(rtbi_query, query_update_account_params)
            rtbi = self.env.cr.fetchone()
            if rtbi:
                extra_initial_balance = rtbi[0]
                acc.initial_balance = extra_initial_balance
                custom_balance = (
                    acc.final_debit - acc.initial_debit
                ) - (acc.final_credit - acc.initial_credit)
                acc.period_balance = custom_balance
                acc.final_balance = (
                    extra_initial_balance + custom_balance
                )

    def _inject_account_values(self):
        """Inject report values for report_general_ledger_account."""
        query_inject_account = """
WITH
    accounts AS
        (
            SELECT
                a.id,
                a.code,
                a.name,
                a.internal_type IN ('payable', 'receivable')
                    AS is_partner_account,
                a.user_type_id,
                a.currency_id
            FROM
                account_account a
            """
        if (
            self.filter_partner_ids
            or self.filter_cost_center_ids
            or self.filter_analytic_tag_ids
        ):
            query_inject_account += """
            INNER JOIN
                account_move_line ml ON a.id = ml.account_id
            """
        if self.filter_partner_ids:
            query_inject_account += """
            INNER JOIN
                res_partner p ON ml.partner_id = p.id
            """
        if self.filter_cost_center_ids:
            query_inject_account += """
            INNER JOIN
                account_analytic_account aa
                    ON
                        ml.analytic_account_id = aa.id
                        AND aa.id IN %s
            """
        if self.filter_analytic_tag_ids:
            query_inject_account += """
            INNER JOIN
                account_analytic_tag_account_move_line_rel atml
                    ON atml.account_move_line_id = ml.id
            INNER JOIN
                account_analytic_tag aat
                    ON
                        atml.account_analytic_tag_id = aat.id
                        AND aat.id IN %s
            """
        query_inject_account += """
            WHERE
                a.company_id = %s
            AND a.id != %s
                    """
        if self.filter_account_ids:
            query_inject_account += """
            AND
                a.id IN %s
            """
        if self.filter_partner_ids:
            query_inject_account += """
            AND
                p.id IN %s
            """
        if (
            self.filter_partner_ids
            or self.filter_cost_center_ids
            or self.filter_analytic_tag_ids
        ):
            query_inject_account += """
            GROUP BY
                a.id
            """
        query_inject_account += """
        ),
        """
        if self.filter_analytic_tag_ids:
            query_inject_account += """
        move_lines_on_tags AS
            (
                SELECT
                    DISTINCT ml.id AS ml_id
                FROM
                    accounts a
                INNER JOIN
                    account_move_line ml
                        ON a.id = ml.account_id
                INNER JOIN
                    account_analytic_tag_account_move_line_rel atml
                        ON atml.account_move_line_id = ml.id
                INNER JOIN
                    account_analytic_tag aat
                        ON
                            atml.account_analytic_tag_id = aat.id
                WHERE
                    aat.id IN %s
            ),
                """

        init_subquery = (
            self._get_final_account_sub_subquery_sum_amounts(
                date_included=False
            )
        )
        final_subquery = (
            self._get_final_account_sub_subquery_sum_amounts(
                date_included=True
            )
        )

        query_inject_account += (
            """
    initial_sum_amounts AS ( """
            + init_subquery
            + """ ),
    final_sum_amounts AS ( """
            + final_subquery
            + """ )
INSERT INTO
    report_general_ledger_account
    (
    report_id,
    create_uid,
    create_date,
    account_id,
    code,
    name,
    initial_debit,
    initial_credit,
    initial_balance,
    currency_id,
    initial_balance_foreign_currency,
    final_debit,
    final_credit,
    final_balance,
    final_balance_foreign_currency,
    is_partner_account
    )
SELECT
    %s AS report_id,
    %s AS create_uid,
    NOW() AS create_date,
    a.id AS account_id,
    a.code,
    a.name,
    COALESCE(i.debit, 0.0) AS initial_debit,
    COALESCE(i.credit, 0.0) AS initial_credit,
    COALESCE(i.balance, 0.0) AS initial_balance,
    c.id AS currency_id,
    COALESCE(i.balance_currency, 0.0) AS initial_balance_foreign_currency,
    COALESCE(f.debit, 0.0) AS final_debit,
    COALESCE(f.credit, 0.0) AS final_credit,
    COALESCE(f.balance, 0.0) AS final_balance,
    COALESCE(f.balance_currency, 0.0) AS final_balance_foreign_currency,
    a.is_partner_account
FROM
    accounts a
LEFT JOIN
    initial_sum_amounts i ON a.id = i.account_id
LEFT JOIN
    final_sum_amounts f ON a.id = f.account_id
LEFT JOIN
    res_currency c ON c.id = a.currency_id
WHERE
    (
        i.debit IS NOT NULL AND i.debit != 0
        OR i.credit IS NOT NULL AND i.credit != 0
        OR i.balance IS NOT NULL AND i.balance != 0
        OR f.debit IS NOT NULL AND f.debit != 0
        OR f.credit IS NOT NULL AND f.credit != 0
        OR f.balance IS NOT NULL AND f.balance != 0
    )
        """
        )
        if self.hide_account_at_0:
            query_inject_account += """
AND
    f.balance IS NOT NULL AND f.balance != 0
            """
        query_inject_account_params = ()
        if self.filter_cost_center_ids:
            query_inject_account_params += (
                tuple(self.filter_cost_center_ids.ids),
            )
        if self.filter_analytic_tag_ids:
            query_inject_account_params += (
                tuple(self.filter_analytic_tag_ids.ids),
            )
        query_inject_account_params += (
            self.company_id.id,
            self.unaffected_earnings_account.id,
        )
        if self.filter_account_ids:
            query_inject_account_params += (
                tuple(self.filter_account_ids.ids),
            )
        if self.filter_partner_ids:
            query_inject_account_params += (
                tuple(self.filter_partner_ids.ids),
            )
        if self.filter_analytic_tag_ids:
            query_inject_account_params += (
                tuple(self.filter_analytic_tag_ids.ids),
            )

        if self.usd_amount:
            query_inject_account_params += (
                self.exchange_rate_amount,
                self.exchange_rate_amount,
                self.exchange_rate_amount,
            )

        query_inject_account_params += (
            self.date_from,
            self.fy_start_date,
        )
        if self.filter_cost_center_ids:
            query_inject_account_params += (
                tuple(self.filter_cost_center_ids.ids),
            )

        if self.usd_amount:
            query_inject_account_params += (
                self.exchange_rate_amount,
                self.exchange_rate_amount,
                self.exchange_rate_amount,
            )

        query_inject_account_params += (self.date_from,)
        if self.filter_cost_center_ids:
            query_inject_account_params += (
                tuple(self.filter_cost_center_ids.ids),
            )

        if self.usd_amount:
            query_inject_account_params += (
                self.exchange_rate_amount,
                self.exchange_rate_amount,
                self.exchange_rate_amount,
            )

        query_inject_account_params += (
            self.date_to,
            self.fy_start_date,
        )
        if self.filter_cost_center_ids:
            query_inject_account_params += (
                tuple(self.filter_cost_center_ids.ids),
            )

        if self.usd_amount:
            query_inject_account_params += (
                self.exchange_rate_amount,
                self.exchange_rate_amount,
                self.exchange_rate_amount,
            )

        query_inject_account_params += (self.date_to,)
        if self.filter_cost_center_ids:
            query_inject_account_params += (
                tuple(self.filter_cost_center_ids.ids),
            )
        query_inject_account_params += (
            self.id,
            self.env.uid,
        )

        self.env.cr.execute(
            query_inject_account, query_inject_account_params
        )
