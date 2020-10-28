# Copyright 2020 Calyx
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountAssetFACPCE(models.Model):
    _name = "account.asset.facpce"
    _description = "Assets Inflation FACPCE Coefficient"
    _order = "date_start desc, name"

    name = fields.Char()

    date_start = fields.Date(
        string="Start Date",
        required=True,
        default=lambda self: datetime.today().replace(day=1),
        help="Start Date of the FACPCE Inflation Index",
    )

    date_end = fields.Date(
        string="End Date",
        required=True,
        default=lambda self: (datetime.today().replace(day=1) + relativedelta(months=+1)),
        help="End Date of the FACPCE Inflation Index",
    )

    inflation_coefficient = fields.Float(
        string="Index",
        digits=(4, 4),
        required=True
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self._default_company_id(),
    )

    @api.model
    def _default_company_id(self):
        return self.env.company

    @api.model
    def create(self, vals):
        if vals.get('name'):
            vals.update({'name': vals['name'].capitalize()})
        return super(AccountAssetFACPCE, self).create(vals)

    def write(self, vals):
        if vals.get('name'):
            vals.update({'name': vals['name'].capitalize()})
        return super(AccountAssetFACPCE, self).write(vals)

    @api.constrains('date_start', 'date_end', 'company_id')
    def _check_dates(self):
        '''
        Check interleaving between fiscal years.
        There are 3 cases to consider:

        s1   s2   e1   e2
        (    [----)----]

        s2   s1   e2   e1
        [----(----]    )

        s1   s2   e2   e1
        (    [----]    )
        '''
        for fy in self:
            # Starting date must be prior to the ending date
            date_start = fy.date_start
            date_end = fy.date_end
            if date_end < date_start:
                raise ValidationError(_('The ending date must not be prior to the starting date.'))


            domain = [
                ('id', '!=', fy.id),
                ('company_id', '=', fy.company_id.id),
                '|', '|',
                '&', ('date_start', '<=', fy.date_start), ('date_end', '>=', fy.date_start),
                '&', ('date_start', '<=', fy.date_end), ('date_end', '>=', fy.date_end),
                '&', ('date_start', '<=', fy.date_start), ('date_end', '>=', fy.date_end),
            ]

            if self.search_count(domain) > 0:
                raise ValidationError(_('You can not have an overlap between two fiscal years, please correct the start and/or end dates of your fiscal years.'))

