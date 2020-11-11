# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountFiscalYear(models.Model):
    _inherit = "account.fiscal.year"

    fiscal_year_close = fields.Boolean(
        string="Fiscal Year Close", default=False
    )
