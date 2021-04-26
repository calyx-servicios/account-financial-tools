# Copyright 2020 Calyx
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _


class AccountAssetLine(models.Model):
    _inherit = "account.asset.line"

    inflation_coefficient = fields.Float(
        string="Inflation Coefficient",
        digits=(2, 2),
        store=True
    )

    inflation_coefficient_status = fields.Char(
        string="FACPCE Coefficient",
    )

    historical_value = fields.Float(
        string="Historical Value",
        digits=(2, 2),
        compute="_compute_inflation_values",
        store=True
    )

    historical_value_result = fields.Float(
        string="Historical Value With Inflation",
        digits=(2, 2),
        store=True
    )

    inflation_adjustment = fields.Float(
        digits=(2, 2),
        compute="_compute_inflation_adjustment",
        store=True
    )

    depreciated_value_result = fields.Float(
        string="Depreciated Value With Inflation",
        digits=(2, 2),
        store=True
    )

    depreciated_adjustment = fields.Float(
        digits=(2, 2),
        store=True
    )

    def write(self, vals):
        facpce_index_end = self.env['account.asset.facpce'].search([
            ('date_start', '<=', self.line_date),
            ('date_end', '>=', self.line_date),
            ('company_id', '=', self.env.user.company_id.id)
        ], limit=1)

        facpce_index_start = self.env['account.asset.facpce'].search([
            ('date_start', '<=', self.line_date + relativedelta(months=-1)),
            ('date_end', '>=', self.line_date + relativedelta(months=-1)),
            ('company_id', '=', self.env.user.company_id.id)
        ], limit=1)

        if facpce_index_end and facpce_index_start:
            vals['inflation_coefficient_status'] = str(round(facpce_index_end.inflation_coefficient /
                                                             facpce_index_start.inflation_coefficient, 2))
            vals['inflation_coefficient'] = round(facpce_index_end.inflation_coefficient /
                                                  facpce_index_start.inflation_coefficient, 2)
        else:
            vals.update({'inflation_coefficient_status': _("FACPCE Coefficient Doesn't Exist")})

        if self.previous_id:
            vals.update(
                {'historical_value_result': round(self.previous_id.historical_value_result * vals.get('inflation_coefficient', 1), 2)})
        elif self.line_days > 0 and self.depreciated_value == 0.00:
            vals.update({'historical_value_result': round((self.depreciation_base * vals.get('inflation_coefficient', 1)), 2)})
            inflation = round(vals.get('historical_value_result') - self.asset_id.depreciation_base, 2)
            vals.update({'inflation_adjustment': inflation})
        else:
            vals.update({'historical_value': self.depreciation_base,
                         'historical_value_result': self.depreciation_base,
                         'inflation_coefficient_status': '0.00'})

        """
            This if statement computes all the lines again in case that
            the historical_value of any line is zero because there is a
            bug in account_asset_management code base when sometimes
            the base depreciation value is zero and the write method
            save it anyways.
        """
        if vals.get('historical_value_result') == 0:
            self.env['account.asset'].browse(self.asset_id.id).compute_depreciation_board()

        if self.depreciated_value > 0 and self.inflation_coefficient > 0:
            depreciated_value_result = round(self.depreciated_value * self.inflation_coefficient, 2)
            vals.update({'depreciated_value_result': depreciated_value_result})
            depreciated_adjustment = round(vals.get('depreciated_value_result', False) - self.depreciated_value, 2)
            vals.update({'depreciated_adjustment': depreciated_adjustment})

        return super().write(vals)

    @api.depends("line_date", "amount", "previous_id", "type")
    def _compute_inflation_values(self):
        for line in self:
            line.write({'historical_value': line.asset_id.depreciation_base})

    @api.depends("historical_value", "inflation_coefficient", "historical_value_result")
    def _compute_inflation_adjustment(self):
        for line in self:
            if line.historical_value_result > line.historical_value:
                res = round((line.historical_value_result - line.historical_value), 2)
                line.write({'inflation_adjustment': res})
