# coding: utf-8
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import logging

from odoo.exceptions import ValidationError
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class AccountPaymentGroup(models.Model):
    _inherit = "account.payment.group"

    amount_total_without_withholdings = fields.Monetary(
        compute='_compute_amount_ww',
        string='Amount Without Withholdings',
        track_visibility='always',
    )

    @api.multi
    @api.depends('selected_debt', 'unreconciled_amount', 'payment_ids')
    def _compute_amount_ww(self):
        for rec in self:
            ww = 0.0
            for payment in rec.payment_ids:
                if payment.tax_withholding_id.tax_group_id.type == 'withholding':
                    continue
                else:
                    ww = payment.signed_amount_company_currency + ww
            rec.amount_total_without_withholdings = ww

    @api.multi
    def post(self):
        for rec in self:
            count = 0
            for payment in self.payment_ids:
                if payment.tax_withholding_id and payment.currency_id == self.env.ref(
                        'base.ARS'
                ) and payment.tax_withholding_id.withholding_type == 'tabla_ganancias':
                    count += 1
                    if payment.payment_type_copy == 'outbound' and payment.amount <= 240:
                        raise ValidationError(
                            _("El monto retenido para ganacias RG830 no puede ser menor a $240"
                              ))
            if len(self.payment_ids) == count:
                raise ValidationError(
                    _("You must include payment line that are not retentions"))
        return super(AccountPaymentGroup, self).post()

    #
    # Withholding summay for Payment Group Tree View
    #

    withholdings_summary = fields.Char(
        readonly=True,
        translate=True,
        compute='_compute_witholdings_summary',
        store=True)

    @api.one
    @api.depends('payments_amount', 'payment_ids.payment_method_description')
    def _compute_witholdings_summary(self):
        withholding_map = {}
        withholding_amount = ''
        for payment in self.payment_ids:
            if payment.journal_id.name.upper() == 'RETENCIONES':

                if payment.payment_method_description not in withholding_map.keys():
                    withholding_map.update({payment.payment_method_description: payment.signed_amount_company_currency})
                else:
                    withholding_map[payment.payment_method_description] += payment.signed_amount_company_currency

        for method, amount in withholding_map.items():
            withholding_amount += '{}: ${}\n'.format(method, round(amount, 2))

        self.withholdings_summary = withholding_amount
