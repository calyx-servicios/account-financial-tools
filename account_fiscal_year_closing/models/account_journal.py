# coding: utf-8
from odoo import models, fields, api, _


class AccountJournal(models.Model):
    _inherit = "account.journal"

    recasting_journal = fields.Boolean(
        "Journal to recasting exercise", default=False
    )

    consolidation_results_journal = fields.Boolean(
        "Journal to consolidation results exercise", default=False
    )
    equity_closing_journal = fields.Boolean(
        "Journal to closing equity exercise", default=False
    )

    equity_opening_journal = fields.Boolean(
        "Journal to opening fiscal year exercise", default=False
    )

    @api.onchange("recasting_journal")
    def _onchange_recasting_journal(self):
        for rec in self:
            acc_obj = self.search([("recasting_journal", "=", True)])
            if rec.recasting_journal:
                if acc_obj:
                    error_string = _(
                        "Already exist another recasting journal (%r)."
                    ) % (acc_obj.name)
                    self.env.user.notify_warning(error_string, "Error")
                    rec.recasting_journal = False

    @api.onchange("consolidation_results_journal")
    def _onchange_consolidation_results_journal(self):
        for rec in self:
            acc_obj = self.search(
                [("consolidation_results_journal", "=", True)]
            )
            if rec.consolidation_results_journal:
                if acc_obj:
                    error_string = _(
                        "Already exist another consolidation results journal (%r)."
                    ) % (acc_obj.name)
                    self.env.user.notify_warning(error_string, "Error")
                    rec.consolidation_results_journal = False

    @api.onchange("equity_closing_journal")
    def _onchange_equity_closing_journal(self):
        for rec in self:
            acc_obj = self.search(
                [("equity_closing_journal", "=", True)]
            )
            if rec.equity_closing_journal:
                if acc_obj:
                    error_string = _(
                        "Already exist another equity closing journal (%r)."
                    ) % (acc_obj.name)
                    self.env.user.notify_warning(error_string, "Error")
                    rec.equity_closing_journal = False

    @api.onchange("equity_opening_journal")
    def _onchange_equity_opening_journal(self):
        for rec in self:
            acc_obj = self.search(
                [("equity_opening_journal", "=", True)]
            )
            if rec.equity_opening_journal:
                if acc_obj:
                    error_string = _(
                        "Already exist another equity opening journal (%r)."
                    ) % (acc_obj.name)
                    self.env.user.notify_warning(error_string, "Error")
                    rec.equity_opening_journal = False
