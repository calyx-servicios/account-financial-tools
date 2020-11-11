# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, datetime
from odoo import api, fields, models


class AccountGroup(models.Model):
    """ Here, we just define methods.
    For class fields, go more top at this file.
    """
    _inherit = 'account.group'

    sequence = fields.Integer(index=True, default=1)

