# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, datetime
from odoo import api, fields, models


class AccountDepartment(models.Model):
    _name = "account.department"

    _order = 'code_sufix'

    name = fields.Char(required=True)
    code_sufix = fields.Char(required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get('account.department'))

    _sql_constraints = [
            ('code_company_uniq', 'unique (code_sufix,company_id)', 'The code sufix of the department must be unique per company !')
        ]