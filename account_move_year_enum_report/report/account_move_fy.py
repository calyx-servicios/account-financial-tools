# -*- coding: utf-8 -*-

from odoo import api, models


class AccountMoveFyReport(models.AbstractModel):
    _name = "report.account_move_year_enum_report.report_account_fy"

    @api.model
    def get_report_values(self, docids, data=None):

        return {
            "doc_ids": data["move_ids"],
            "doc_model": self.env["account.move"],
            "data": data,
            "docs": self.env["account.move"].browse(data["move_ids"]),
        }
