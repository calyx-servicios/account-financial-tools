# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,date,timedelta
from dateutil import relativedelta

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def post(self):
        config_param = self.env['ir.config_parameter'].search([('key','=','LIMIT_ACCOUNT_POST_DAYS')])
        previous_date = date.today()
        days_parm = 0
        try:
    	    if config_param:
                days_parm = int(config_param.value)
                previous_date = date.today() - timedelta(days=days_parm)
        except:
            pass
        if config_param:
            for am in self:
                if am.date:
                    if days_parm == 0:
                        current_month = int(datetime.now().strftime("%m"))
                        if int(am.date[5:7]) != current_month:
                            raise ValidationError('No se puede realizar un movimiento contable tan en el mes anterior')
                    elif days_parm > 0:
                        posting_month = int(am.date[5:7])
                        today = date.today()
                        if posting_month != today.month:
                            if days_parm < today.day:
                                raise ValidationError('No se puede realizar un movimiento contable tan en el pasado')
                    elif am.date < str(previous_date):
                        raise ValidationError('No se puede realizar un movimiento contable tan en el pasado')
                    else:
                        pass
        res = super(AccountMove, self).post()
        return res


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        config_param = self.env['ir.config_parameter'].search([('key','=','LIMIT_ACCOUNT_POST_DAYS')])
        previous_date =	date.today()
        days_parm = 0
        try:
            if config_param:
                days_parm = int(config_param.value)
                previous_date = date.today() - timedelta(days=days_parm)
        except:
            pass
        if config_param and self.date_invoice:
            for inv in self:
                if inv.type in ['out_invoice','out_refund'] or not inv.date:
                    date_invoice = inv.date_invoice
                else:
                    date_invoice = inv.date
                if days_parm == 0:
                    current_month = int(datetime.now().strftime("%m"))
                    if int(date_invoice[5:7]) != current_month:
                        raise ValidationError('No se puede realizar un movimiento contable tan en el mes anterior')
                elif days_parm > 0:
                    posting_month = int(date_invoice[5:7])
                    today = date.today()
                    if posting_month != today.month:
                        if days_parm < today.day:
                            raise ValidationError('No se puede realizar un movimiento contable tan en el pasado')
                elif date_invoice < str(previous_date):
                    raise ValidationError('No se puede realizar un movimiento contable tan en el pasado')
                else:
                    pass
        res = super(AccountInvoice, self).action_invoice_open()
        return res

	
class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def post(self):
        config_param = self.env['ir.config_parameter'].search([('key','=','LIMIT_ACCOUNT_POST_DAYS')],limit=1)
        previous_date = date.today()
        days_parm = 0
        try:
            if config_param:
                days_parm = int(config_param.value)
                previous_date = date.today() - timedelta(days=days_parm)
        except:
            pass
        if config_param:
            for pay in self:
                if not pay.payment_date:
                    continue
                if days_parm == 0:
                    current_month = int(datetime.now().strftime("%m"))
                    if int(pay.payment_date[5:7]) != current_month:
                        raise ValidationError('No se puede realizar un movimiento contable tan en el mes anterior')
                    elif days_parm > 0:
                        posting_month = int(pay.payment_date[5:7])
                        today = date.today()
                        if posting_month != today.month:
                            if days_parm < today.day:
                                raise ValidationError('No se puede realizar un movimiento contable tan en el pasado')
                    elif pay.payment_date < str(previous_date):
                        raise ValidationError('No se puede realizar un movimiento contable tan en el pasado')
                    else:
                        pass
        res = super(AccountPayment, self).post()
        return res
