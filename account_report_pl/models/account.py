from odoo import fields, models, _
from odoo.exceptions import Warning

class AccountAccount(models.Model):
    _inherit = 'account.account'

    report_pl_id = fields.Many2one('report.pl', string="Report P&L")

