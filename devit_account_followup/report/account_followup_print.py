# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from collections import defaultdict
from odoo.exceptions import ValidationError

from odoo import api, fields, models, _


# from openerp.report import report_sxw


class ReportRappel(models.AbstractModel):
    _name = 'report.devit_account_followup.report_followup'

    @api.model
    def get_report_values(self, docids, data=None):
        model = self.env['devit_account_followup.sending.results']
        ids = self.env.context.get('active_ids') or False
        docs = model.browse(ids)
        return {
            'docs': docs,
            'doc_ids': docids,
            'doc_model': model,
            'time': time,
            'ids_to_objects': self._ids_to_objects,
            'getLines': self._lines_get,
            'get_text': self._get_text,
            'data': data and data['form'] or {}}

    def _ids_to_objects(self, ids):
        all_lines = []
        for line in self.env['devit_account_followup.stat.by.partner'].browse(ids):
            if line not in all_lines:
                all_lines.append(line)
        return all_lines

    def _lines_get(self, stat_by_partner_line):
        return self._lines_get_with_partner(stat_by_partner_line.partner_id,
                                            stat_by_partner_line.company_id.id)

    def _lines_get_with_partner(self, partner, company_id):
        moveline_obj = self.env['account.move.line']
        moveline_ids = moveline_obj.search(
            [('partner_id', '=', partner.id),
             ('account_id.user_type_id.type', '=', 'receivable'),
             ('full_reconcile_id', '=', False),
             ('company_id', '=', company_id),
             '|', ('date_maturity', '=', False),
             ('date_maturity', '<=', fields.Date.today())])

        # lines_per_currency = {currency: [line data, ...], ...}
        lines_per_currency = defaultdict(list)
        total = 0
        for line in moveline_ids:
            currency = line.currency_id or line.company_id.currency_id
            balance = line.debit - line.credit
            if currency != line.company_id.currency_id:
                balance = line.amount_currency
            line_data = {
                'name': line.move_id.name,
                'invoice_display_name': line.invoice_id.display_name or line.move_id.display_name,
                'ref': line.ref,
                'date': line.date,
                'date_invoice': line.invoice_id.date_invoice,
                'date_maturity': line.date_maturity,
                'balance': balance,
                'blocked': line.blocked,
                'currency_id': currency,
            }
            total = total + line_data['balance']
            lines_per_currency[currency].append(line_data)

        return [{'total': total, 'line': lines, 'currency': currency} for
                currency, lines in
                lines_per_currency.items()]

    def _get_text(self, stat_line, followup_id, context=None):
        context = dict(context or {}, lang=stat_line.partner_id.lang)
        fp_obj = self.env['devit_account_followup.followup']
        fp_line = fp_obj.browse(followup_id).followup_line
        if not fp_line:
            raise ValidationError(
                _("The followup plan defined for the current company does not "
                  "have any followup action."))
        # the default text will be the first fp_line in the sequence with a
        # description.
        default_text = ''
        li_delay = []
        for line in fp_line:
            if not default_text and line.description:
                default_text = line.description
            li_delay.append(line.delay)
        li_delay.sort(reverse=True)
        # look into the lines of the partner that already have a
        # followup level, and take the description of the higher level
        # for which it is available
        partner_line_ids = self.env['account.move.line'].search(
            [('partner_id', '=', stat_line.partner_id.id),
             ('full_reconcile_id', '=', False),
             ('company_id', '=', stat_line.company_id.id),
             ('blocked', '=', False),
             ('debit', '!=', False),
             ('account_id.user_type_id.type', '=', 'receivable'),
             ('followup_line_id', '!=', False)])
        partner_max_delay = 0
        partner_max_text = ''
        for i in partner_line_ids:
            if i.followup_line_id.delay > partner_max_delay and \
                    i.followup_line_id.description:
                partner_max_delay = i.followup_line_id.delay
                partner_max_text = i.followup_line_id.description
        text = partner_max_delay and partner_max_text or default_text
        if text:
            lang_obj = self.env['res.lang']
            lang_ids = lang_obj.search(
                [('code', '=', stat_line.partner_id.lang)], limit=1)
            date_format = lang_ids and lang_ids.date_format or '%Y-%m-%d'
            text = text % {
                'partner_name': stat_line.partner_id.name,
                'date': time.strftime(date_format),
                'company_name': stat_line.company_id.name,
                'user_signature': self.env.user.signature or '',
            }
        return text
