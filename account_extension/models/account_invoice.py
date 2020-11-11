##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import re
import logging

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    date = fields.Date(string='Accounting Date',
                       default=fields.Date.today,
                       copy=False,
                       readonly=True, states={'draft': [('readonly', False)]})

    @api.onchange('document_number')
    def onchange_document_number(self):
        if self.document_number:
            document_number_split = (self.document_number).split('-')
            if len(document_number_split) != 2:
                raise ValidationError(
                    _("You put (%s) and Document Number must be whit a '-' in middle.") % (self.document_number))

            while len(document_number_split[0]) < 4:
                document_number_split[0] = '0' + document_number_split[0]
            while len(document_number_split[1]) < 8:
                document_number_split[1] = '0' + document_number_split[1]

            document_control = document_number_split[0] + '-' + document_number_split[1]

            self_ids = self.search(
                [('partner_id', '=', self.partner_id.id), ('document_number', '=', document_control), ])
            if len(self_ids) != 0:
                raise ValidationError(_('Check Number (%s) must be unique per Partner!') % (document_control))

    @api.multi
    def action_invoice_draft(self):
        self.ensure_one()
        account_date = self.date
        super().action_invoice_draft()
        self.date = account_date
        return True
