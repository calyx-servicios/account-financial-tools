# Copyright 2020 Calyx
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _

READONLY_STATES = {
    "open": [("readonly", True)],
    "close": [("readonly", True)],
    "removed": [("readonly", True)],
}


class AccountAsset(models.Model):
    _inherit = "account.asset"

    inflation_line_ids = fields.One2many(
        comodel_name="account.asset.line",
        inverse_name="asset_id",
        string="Inflation Lines",
        copy=False,
        states=READONLY_STATES,
    )

