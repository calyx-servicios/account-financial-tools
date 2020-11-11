# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, datetime
from odoo import _,api, fields, models
import logging
_logger = logging.getLogger(__name__)

class GeneralLedgerXslx(models.AbstractModel):
    _inherit = 'report.a_f_r.report_general_ledger_xlsx'


    def _generate_report_content(self, workbook, report):
        # For each account
        _logger.debug('GeneralLedgeReport XLS====> ')
        if not report.show_ungroup:
            super(GeneralLedgerXslx, self)._generate_report_content(workbook, report)
        else:
            for account in report.account_ids:
                if not account.partner_ids:
                    self.write_initial_balance_custom(account)
                    for line in account.move_line_ids:
                            self.write_line(line)
                else:
                    for partner in account.partner_ids:
                        self.write_initial_balance_custom(partner)
                        for line in partner.move_line_ids:
                            self.write_line(line)



    def _get_report_columns(self, report):
        if not report.show_ungroup:
            res = super(GeneralLedgerXslx, self)._get_report_columns(report)
        else:
            res = {
                0: {'header': _('Date'), 'field': 'date', 'width': 11},
                1: {'header': _('Entry'), 'field': 'entry', 'width': 18},
                2: {'header': _('Journal'), 'field': 'journal', 'width': 8},
                3: {'header': _('Account'), 'field': 'account','width': 9},
                4: {'header': _('Account Name'), 'field': 'account_name', 'field_initial_balance': 'name', 'width': 9},
                5: {'header': _('Display Name'), 'field': 'entry_name', 'width': 9},
                6: {'header': _('Taxes'),
                    'field': 'taxes_description',
                    'width': 15},
                7: {'header': _('Partner'), 'field': 'partner', 'width': 25},
                8: {'header': _('Ref - Label'), 'field': 'label', 'width': 40},
                9: {'header': _('Cost center'),
                    'field': 'center_name',
                    'width': 15},
                10: {'header': _('Tags'),
                    'field': 'tags',
                    'width': 10},
                11: {'header': _('Rec.'), 'field': 'matching_number', 'width': 5},
                12: {'header': _('Debit'),
                    'field': 'debit',
                    'field_initial_balance': 'initial_debit',
                    'field_final_balance': 'final_debit',
                    'type': 'amount',
                    'width': 14},
                13: {'header': _('Credit'),
                    'field': 'credit',
                    'field_initial_balance': 'initial_credit',
                    'field_final_balance': 'final_credit',
                    'type': 'amount',
                    'width': 14},
                14: {'header': _('Cumul. Bal.'),
                    'field': 'cumul_balance',
                    'field_initial_balance': 'initial_balance',
                    'field_final_balance': 'final_balance',
                    'type': 'amount',
                    'width': 14},
            }
            if report.foreign_currency:
                foreign_currency = {
                    15: {'header': _('Cur.'),
                        'field': 'currency_id',
                        'field_currency_balance': 'currency_id',
                        'type': 'many2one', 'width': 7},
                    16: {'header': _('Amount cur.'),
                        'field': 'amount_currency',
                        'field_initial_balance':
                            'initial_balance_foreign_currency',
                        'field_final_balance':
                            'final_balance_foreign_currency',
                        'type': 'amount_currency',
                        'width': 14},
                }
                res = {**res, **foreign_currency}
        return res


    def write_initial_balance_custom(self, my_object):
        """Write a specific initial balance line on current line
        using defined columns field_initial_balance name.

        Columns are defined with `_get_report_columns` method.
        """
        if 'partner' in my_object._name:
            label = _('Partner Initial balance')
            my_object.currency_id = my_object.report_account_id.currency_id
        elif 'account' in my_object._name:
            label = _('Initial balance')
        col_pos_label = self._get_col_pos_initial_balance_label()
        self.sheet.write(self.row_pos, col_pos_label, label, self.format_right)

        for col_pos, column in self.columns.items():
            if column.get('field_initial_balance'):
                value = getattr(my_object, column['field_initial_balance'])
                cell_type = column.get('type', 'string')
                if cell_type == 'string':
                    self.sheet.write_string(self.row_pos, col_pos, value or '')
                elif cell_type == 'amount':
                    self.sheet.write_number(
                        self.row_pos, col_pos, float(value), self.format_amount
                    )
                elif cell_type == 'amount_currency':
                    if my_object.currency_id:
                        format_amt = self._get_currency_amt_format(
                            my_object)
                        self.sheet.write_number(
                            self.row_pos, col_pos,
                            float(value), format_amt
                        )
            elif column.get('field_currency_balance'):
                value = getattr(my_object, column['field_currency_balance'])
                cell_type = column.get('type', 'string')
                if cell_type == 'many2one':
                    if my_object.currency_id:
                        self.sheet.write_string(
                            self.row_pos, col_pos,
                            value.name or '',
                            self.format_right
                        )
        self.row_pos += 1
