# Copyright 2020 Calyx
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountAsset(models.Model):
    _inherit = "account.asset"

    depreciated_value_sap = fields.Float(
        string="Depreciated Value SAP", digits=(2, 2)
    )

    residual_value_sap = fields.Float(
        string="Residual Value SAP", digits=(2, 2)
    )

    accumulated_depreciation_sap = fields.Float(
        string="Accumulated Depr. SAP", digits=(2, 2)
    )

    book_value_sap = fields.Float(
        string="Book Value SAP", digits=(2, 2)
    )

    monthl_sap = fields.Float(string="Month SAP", digits=(2, 2))

    cost_center_sap = fields.Float(
        string="Cost Center SAP", digits=(2, 2)
    )
