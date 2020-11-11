# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, datetime
from odoo import _,api, fields, models
import logging
_logger = logging.getLogger(__name__)

class DepartmentXslx(models.AbstractModel):
    _inherit = 'report.a_f_r.report_trial_balance_xlsx'

    sheets = None
    current = None

    def _get_report_name(self, report):
        if not report.by_department:
            return super(DepartmentXslx, self)._get_report_name(report)
        else:
            report_name = _('Department Balance')
            return self._get_report_complete_name(report, report_name)

    def generate_xlsx_report(self, workbook, data, objects):
        report = objects
        if report.by_month:



            self.row_pos = 0

            self._define_formats(workbook)

            report_name = self._get_report_name(report)
            report_footer = self._get_report_footer()
            filters = self._get_report_filters(report)
            self.columns = self._get_report_columns(report)
            self.workbook = workbook
            # self.sheet = workbook.add_worksheet(report_name[:31])
            #
            # self._set_column_width()
            # self._write_report_title(report_name)
            # self._write_filters(filters)
            self._generate_report_content(workbook, report)
            self._write_report_footer(report_footer)
        else:
            super(DepartmentXslx,self).generate_xlsx_report(workbook, data, objects)

    def _generate_report_content_custom(self, workbook, report):

        if not report.show_partner_details and not report.by_month:
            self.write_array_header()

        # For each account
        for account in report.account_ids.filtered(lambda a: not a.hide_line):
            if not report.show_partner_details:
                # Display account lines
                self.write_line(account, 'account', report)

            else:
                # Write account title
                self.write_array_title(account.code + ' - ' + account.name)

                # Display array header for partner lines
                self.write_array_header()

                # For each partner
                for partner in account.partner_ids:
                    # Display partner lines
                    self.write_line(partner, 'partner',report)

                # Display account footer line
                self.write_account_footer(account,
                                          account.code + ' - ' + account.name)

                # Line break
                self.row_pos += 2

    def _generate_report_content(self, workbook, report):
        if report.by_month:
            self.sheets = {}
            self.current=''
        # For each account
        if not report.by_department:
            # _logger.debug('=====>>>>Report?: %s ' % report)
            # for month in report.general_ledger_id.month_ids:
            #     _logger.debug('Month: %s ' % month.name)
            # self.write_array_header()
            #super(DepartmentXslx, self)._generate_report_content(workbook, report)
            self._generate_report_content_custom(workbook, report)
            report_name = self._get_report_name(report)
            report_name = report_name[:31]

        else:

            self.write_array_header()
            for department in report.department_ids:
                self.write_department_title(department)
                for account in department.account_ids:
                    self.write_account(account)
                self.write_department_footer(department)

    def write_department_title(self, department):
        """Write array title on current line using all defined columns width.
        Columns are defined with `_get_report_columns` method.
        """
        col_pos =0
        self.sheet.write_string(
                    self.row_pos, col_pos, department.code_sufix, self.format_bold)
        col_pos += 1
        self.sheet.write_string(
                    self.row_pos, col_pos, department.name, self.format_bold)
        col_pos += 2
        self.sheet.write_number(
                        self.row_pos, col_pos, float(department.initial_balance), self.format_amount_bold)
        col_pos += 1

        self.row_pos += 1

    def write_department_footer(self, department):
        """Write array title on current line using all defined columns width.
        Columns are defined with `_get_report_columns` method.
        """

        col_pos = 2
        name ='Final Balance '+ department.name
        self.sheet.write_string(
                    self.row_pos, col_pos, name, self.format_right)

        col_pos = 6
        self.sheet.write_number(
                        self.row_pos, col_pos, float(department.period_balance), self.format_amount
                    )
        col_pos += 1
        self.sheet.write_number(
                        self.row_pos, col_pos, float(department.final_balance), self.format_amount
                    )
        self.row_pos += 2

    def write_account(self, account):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """
        col_pos =0
        if account.account_id.group_id:
            prefix = account.account_id.group_id.code_prefix or ''
            self.sheet.write_string(
                    self.row_pos, col_pos, prefix, self.format_right)
        col_pos += 1
        self.sheet.write_string(
                    self.row_pos, col_pos, account.code, self.format_right)
        col_pos += 1
        self.sheet.write_string(
                    self.row_pos, col_pos, account.name, self.format_left)
        col_pos += 1
        self.sheet.write_number(
                        self.row_pos, col_pos, float(account.initial_balance), self.format_amount
                    )
        col_pos += 1
        self.sheet.write_number(
                        self.row_pos, col_pos, float(account.debit), self.format_amount
                    )
        col_pos += 1
        self.sheet.write_number(
                        self.row_pos, col_pos, float(account.credit), self.format_amount
                    )
        col_pos += 1
        self.sheet.write_number(
                        self.row_pos, col_pos, float(account.period_balance), self.format_amount
                    )
        col_pos += 1
        self.sheet.write_number(
                        self.row_pos, col_pos, float(account.final_balance), self.format_amount
                    )

        self.row_pos += 1

    def _get_report_columns(self, report):
        if not report.by_department:
            if not report.by_month:
                if not report.show_partner_details:
                    res = {
                        0: {'header': _('Group code'),
                            'field': 'account_group_code_prefix',
                            'width': 10
                            },
                        1: {'header': _('Group'),
                            'field': 'account_gruop_name',
                            'width': 10
                            },
                        2: {'header': _('Code'),
                            'field': 'code',
                            'width': 10
                            },
                        3: {'header': _('Account'),
                            'field': 'name',
                            'width': 60
                            },
                        4: {'header': _('Initial balance'),
                            'field': 'initial_balance',
                            'type': 'amount',
                            'width': 14
                            },
                        5: {'header': _('Debit'),
                            'field': 'debit',
                            'type': 'amount',
                            'width': 14
                            },
                        6: {'header': _('Credit'),
                            'field': 'credit',
                            'type': 'amount',
                            'width': 14
                            },
                        7: {'header': _('Period balance'),
                            'field': 'period_balance',
                            'type': 'amount',
                            'width': 14
                            },
                        8: {'header': _('Ending balance'),
                            'field': 'final_balance',
                            'type': 'amount',
                            'width': 14
                            },
                    }
                    if report.foreign_currency:
                        foreign_currency = {
                            9: {'header': _('Cur.'),
                                'field': 'currency_id',
                                'field_currency_balance': 'currency_id',
                                'type': 'many2one', 'width': 7
                                },
                            10: {'header': _('Initial balance'),
                                'field': 'initial_balance_foreign_currency',
                                'type': 'amount_currency',
                                'width': 14
                                },
                            11: {'header': _('Ending balance'),
                                'field': 'final_balance_foreign_currency',
                                'type': 'amount_currency',
                                'width': 14
                                },
                        }
                        res = {**res, **foreign_currency}
                    return res
                else:
                    res = {
                        0: {'header': _('Partner'), 'field': 'name', 'width': 70},
                        1: {'header': _('Initial balance'),
                            'field': 'initial_balance',
                            'type': 'amount',
                            'width': 14},
                        2: {'header': _('Debit'),
                            'field': 'debit',
                            'type': 'amount',
                            'width': 14},
                        3: {'header': _('Credit'),
                            'field': 'credit',
                            'type': 'amount',
                            'width': 14},
                        4: {'header': _('Period balance'),
                            'field': 'period_balance',
                            'type': 'amount',
                            'width': 14},
                        5: {'header': _('Ending balance'),
                            'field': 'final_balance',
                            'type': 'amount',
                            'width': 14},
                    }
                    if report.foreign_currency:
                        foreign_currency = {
                            6: {'header': _('Cur.'),
                                'field': 'currency_id',
                                'field_currency_balance': 'currency_id',
                                'type': 'many2one', 'width': 7},
                            7: {'header': _('Initial balance'),
                                'field': 'initial_balance_foreign_currency',
                                'type': 'amount_currency',
                                'width': 14},
                            8: {'header': _('Ending balance'),
                                'field': 'final_balance_foreign_currency',
                                'type': 'amount_currency',
                                'width': 14},
                        }
                        res = {**res, **foreign_currency}
                    return res
            elif report.by_month and report.hierarchy_on != 'none':
                res = {
                    0: {'header': _('Code'),
                        'field': 'code',
                        'width': 10
                        },
                    1: {'header': _('Account'),
                        'field': 'name',
                        'width': 60
                        },
                    2: {'header': _('Initial balance'),
                        'field': 'initial_balance',
                        'type': 'amount',
                        'width': 14
                        },
                }
                count = len(res.keys())
                for child in report.child_ids:
                    total = 0
                    month=datetime.strptime(child.date_from,"%Y-%m-%d")
                    month=month.strftime("%b-%Y")
                    column = {count: {'header': _(month),
                        'field': _('period_balance'),
                        'type': 'amount',
                        'report_id': child.id,
                        'width': 14},}
                    res = {**res, **column}
                    count+=1
                column = {count: {'header': _('Ending balance'),
                    'field': 'final_balance',
                    'type': 'amount',
                    'width': 14},
                    }
                res = {**res, **column}
                count+=1
            elif report.by_month and report.hierarchy_on == 'none':
                res = {
                    0: {'header': _('Group code'),
                        'field': 'account_group_code_prefix',
                        'width': 10
                        },
                    1: {'header': _('Group'),
                        'field': 'account_gruop_name',
                        'width': 10
                        },
                    2: {'header': _('Code'),
                        'field': 'code',
                        'width': 10
                        },
                    3: {'header': _('Account'),
                        'field': 'name',
                        'width': 60
                        },
                    4: {'header': _('Initial balance'),
                        'field': 'initial_balance',
                        'type': 'amount',
                        'width': 14
                        },
                }
                count = len(res.keys())
                for child in report.child_ids:
                    month=datetime.strptime(child.date_from,"%Y-%m-%d")
                    month=month.strftime("%b-%Y")
                    column = {count: {'header': _(month),
                        'field': _('period_balance'),
                        'type': 'amount',
                        'report_id': child.id,
                        'width': 14
                        },
                    }
                    res = {**res, **column}
                    count+=1
                # column = {count: {'header': _('Debit'),
                #     'field': 'debit',
                #     'type': 'amount',
                #     'width': 14},
                #     }
                # res = {**res, **column}
                # count+=1
                # column = {count: {'header': _('Credit'),
                #     'field': 'credit',
                #     'type': 'amount',
                #     'width': 14},
                #     }
                # res = {**res, **column}
                # count+=1
                # column = {count: {'header': _('Period balance'),
                #     'field': 'period_balance',
                #     'type': 'amount',
                #     'width': 14},
                #     }
                # res = {**res, **column}
                # count+=1
                column = {count: {'header': _('Ending balance'),
                    'field': 'final_balance',
                    'type': 'amount',
                    'width': 14},
                    }
                res = {**res, **column}
                count+=1
        else:
            res = {
                0: {'header': _('Group'),
                    'field': 'account',
                    'width': 20
                    },
                1: {'header': _('Department'),
                    'field': 'department_id',
                    'width': 30
                    },
                2: {'header': _('Account'),
                    'field': 'account',
                    'width': 50
                    },
                3: {'header': _('Initial balance'),
                    'field': 'initial_balance',
                    'type': 'amount',
                    'width': 14
                    },
                4: {'header': _('Debit'),
                    'field': 'debit',
                    'type': 'amount',
                    'width': 14},
                5: {'header': _('Credit'),
                    'field': 'credit',
                    'type': 'amount',
                    'width': 14
                    },
                6: {'header': _('Period balance'),
                    'field': 'period_balance',
                    'type': 'amount',
                    'width': 14
                    },
                7: {'header': _('Ending balance'),
                    'field': 'final_balance',
                    'type': 'amount',
                    'width': 14
                    },
            }
            if report.foreign_currency:
                foreign_currency = {
                    8: {'header': _('Cur.'),
                        'field': 'currency_id',
                        'field_currency_balance': 'currency_id',
                        'type': 'many2one', 'width': 7
                        },
                    9: {'header': _('Initial balance'),
                        'field': 'initial_balance_foreign_currency',
                        'type': 'amount_currency',
                        'width': 14
                        },
                    10: {'header': _('Ending balance'),
                        'field': 'final_balance_foreign_currency',
                        'type': 'amount_currency',
                        'width': 14
                        },
                }
                res = {**res, **foreign_currency}
        return res

    def get_root_parent(self, account):
        if account.parent_id:
            res=self.get_root_parent(account.parent_id)
        else:
            res=account.name
        return res

    def write_line(self, line_object, type_object, report):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """
        #_logger.debug('===> account_group_id:%s month:%s value:%s => row:%s ' % (self.row_pos))
        report_name = self._get_report_name(report)

        if report.by_month and report.hierarchy_on != 'none':
            key = False
            if line_object.account_group_id:
                group_name=self.get_root_parent(line_object.account_group_id)
                key=group_name

            if not key:
                key=report_name[:31]
                self.sheets[key]={
                    'sheet': self.sheet,
                    'row': self.row_pos
                }
            else:
                key=key[:31]
            if self.current:
                #save current sheet state
                self.sheets[self.current]={
                    'sheet': self.sheet,
                    'row': self.row_pos
                }

            if self.sheets.get(key, None):
                #obtain sheet states from sheets
                self.sheet=self.sheets.get(key)['sheet']
                self.row_pos=self.sheets.get(key)['row']
            else:
                #creates a new sheet
                self.sheet = self.workbook.add_worksheet(key)
                self.row_pos = 1

                filters = self._get_report_filters(report)
                self._set_column_width()

                self._write_report_title(report_name)

                self._write_filters(filters)
                self.sheets[key]={
                        'sheet': self.sheet,
                        'row': self.row_pos
                    }
                if not report.show_partner_details:
                    # Display array header for account lines
                    self.write_array_header()

            self.current=key

            if type_object == 'partner':
                line_object.currency_id = line_object.report_account_id.currency_id
            elif type_object == 'account':
                line_object.currency_id = line_object.currency_id
            for col_pos, column in self.columns.items():
                value = getattr(line_object, column['field'])
                cell_type = column.get('type', 'string')
                if cell_type == 'many2one':
                    self.sheet.write_string(
                        self.row_pos, col_pos, value.name or '', self.format_right)
                elif cell_type == 'string':
                    if hasattr(line_object, 'account_group_id') and \
                            line_object.account_group_id:
                        self.sheet.write_string(self.row_pos, col_pos, value or '',
                                                self.format_bold)
                    else:
                        self.sheet.write_string(self.row_pos, col_pos, value or '')
                elif cell_type == 'amount':
                    if hasattr(line_object, 'account_group_id') and \
                            line_object.account_group_id:
                        cell_format = self.format_amount_bold
                    else:
                        cell_format = self.format_amount
                    self.sheet.write_number(
                        self.row_pos, col_pos, float(value), cell_format
                    )
                    if report.by_month and report.hierarchy_on != 'none':
                        self.write_month_line(line_object, report, col_pos, column)
                elif cell_type == 'amount_currency':
                    if line_object.currency_id:
                        format_amt = self._get_currency_amt_format(line_object)
                        self.sheet.write_number(
                            self.row_pos, col_pos, float(value), format_amt
                        )
            self.row_pos += 1
            # super(DepartmentXslx, self).write_line(line_object, type_object)
            # self.write_month_line(line_object, report)
        elif report.by_month and report.hierarchy_on == 'none':
            key=report_name[:31]
            if self.current:
                #save current sheet state
                self.sheets[self.current]={
                    'sheet': self.sheet,
                    'row': self.row_pos
                }

            if self.sheets.get(key, None):
                #obtain sheet states from sheets
                self.sheet=self.sheets.get(key)['sheet']
                self.row_pos=self.sheets.get(key)['row']
            else:
                #creates a new sheet
                self.sheet = self.workbook.add_worksheet(key)
                self.row_pos = 1

                filters = self._get_report_filters(report)
                self._set_column_width()

                self._write_report_title(report_name)

                self._write_filters(filters)
                self.sheets[key]={
                        'sheet': self.sheet,
                        'row': self.row_pos
                }
                if not report.show_partner_details:
                    # Display array header for account lines
                    self.write_array_header()

            self.current=key

            if type_object == 'partner':
                line_object.currency_id = line_object.report_account_id.currency_id
            elif type_object == 'account':
                line_object.currency_id = line_object.currency_id
            for col_pos, column in self.columns.items():
                value = getattr(line_object, column['field'])
                cell_type = column.get('type', 'string')
                if cell_type == 'many2one':
                    self.sheet.write_string(
                        self.row_pos, col_pos, value.name or '', self.format_right)
                elif cell_type == 'string':
                    if hasattr(line_object, 'account_group_id') and \
                            line_object.account_group_id:
                        self.sheet.write_string(self.row_pos, col_pos, value or '',
                                                self.format_bold)
                    else:
                        self.sheet.write_string(self.row_pos, col_pos, value or '')
                elif cell_type == 'amount':
                    if hasattr(line_object, 'account_group_id') and \
                            line_object.account_group_id:
                        cell_format = self.format_amount_bold
                    else:
                        cell_format = self.format_amount
                    self.sheet.write_number(
                        self.row_pos, col_pos, float(value), cell_format
                    )
                    self.write_month_line_sumas_saldos(line_object, report, col_pos, column)
                elif cell_type == 'amount_currency':
                    if line_object.currency_id:
                        format_amt = self._get_currency_amt_format(line_object)
                        self.sheet.write_number(
                            self.row_pos, col_pos, float(value), format_amt
                        )
            self.row_pos += 1
        else:
            super(DepartmentXslx, self).write_line(line_object, type_object)

    def write_month_line(self, line_object, report, col_pos, column):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """
        cell_format = self.format_amount_bold
        for month in report.child_ids:
            # for col_pos, column in self.columns.items():

            if line_object.account_group_id:
                if column.get('report_id',False) and column['report_id'] == month.id:
                    month_account=self.env['report_trial_balance_account'].search([
                        ('report_id','=',month.id),
                        ('account_group_id','=',line_object.account_group_id.id),])
                        #('account_id','=',line_object.account_id.id)])

                    #_logger.debug('=====write line======account_id:%s|report_id:%s|month_id%s => %s %s' % (line_object.account_group_id.id,report.general_ledger_id.id,month.id,month_account,line_object))
                    value = month_account.final_balance-month_account.initial_balance
                    _logger.debug('===> account_group_id:%s month:%s value:%s => sheet:%s row:%s col%s ' % (line_object.account_group_id.id, month.id, value, self.sheet.get_name(), self.row_pos, col_pos))
                    self.sheet.write_number(
                        self.row_pos, col_pos, float(value), cell_format
                    )

    def write_month_line_sumas_saldos(self, line_object, report, col_pos, column):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """
        cell_format = self.format_amount
        for month in report.child_ids:
            if column.get('report_id',False) and column['report_id'] == month.id:
                month_account=self.env['report_trial_balance_account'].search([
                    ('report_id','=',month.id),
                    ('account_id','=',line_object.account_id.id)])

                value = month_account.period_balance
                self.sheet.write_number(
                    self.row_pos, col_pos, float(value), cell_format
                )