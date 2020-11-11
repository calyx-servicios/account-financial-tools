##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################

from odoo import models, fields


class AccountPaymentGroup(models.Model):
    _inherit = "account.payment"

    main_id_number = fields.Char(
        related='partner_id.main_id_number',
        string="C.U.I.T.",
        readonly=True
    )
