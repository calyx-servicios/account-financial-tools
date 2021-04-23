from odoo import fields, models, _
from odoo.exceptions import Warning


class ReportPL(models.Model):
    _name = "report.pl"
    _rec_name = "concepts"
    _order = "sequence"

    concepts = fields.Char("Concepts")
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
