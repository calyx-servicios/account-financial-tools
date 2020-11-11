# coding: utf-8
from odoo import models, api


class AccountMoveFYReport(models.TransientModel):
    _inherit = "account.move.fiscal.year.report.wizard"

    @api.multi
    def print_account_fy_report(self):
        """
            
        """
        self.ensure_one()
        data = {}
        by_period = False

        # ################
        # Account Query
        # ################
        if self.by_period:

            account_move_objs = self.env["account.move"].search(
                [
                    ("date", ">=", self.date_from),
                    ("date", "<=", self.date_to),
                    ("state", "=", "posted"),
                    ("company_id", "=", self.env.user.company_id.id),
                ],
                order="date asc, numeration asc",
            )
        else:

            account_move_objs = self.env["account.move"].search(
                [
                    ("date", ">=", self.fiscal_year.date_from),
                    ("date", "<=", self.fiscal_year.date_to),
                    ("state", "=", "posted"),
                    ("numeration", "!=", 0),
                ],
                order="date asc, numeration asc",
            )

        # ##########################
        # Data Form
        # ##########################
        if self.by_period:
            by_period = True

        data.update(
            {
                "by_period": by_period,
                "fiscal_year": self.fiscal_year.display_name,
                "date_from": self.date_from,
                "date_to": self.date_to,
            }
        )

        datas = {"move_ids": account_move_objs.ids, "form": data}

        # ############
        # CALL REPORT
        # ############
        return self.env.ref(
            "account_move_year_enum_report.action_report_account_fy"
        ).report_action(self, data=datas)
