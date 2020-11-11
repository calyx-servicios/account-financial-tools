# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, datetime
from odoo import api, fields, models
from odoo.tools import float_is_zero
from datetime import  timedelta
import time
import datetime
from collections import OrderedDict
import logging
_logger = logging.getLogger(__name__)


class DepartmentBalanceReportDepartment(models.TransientModel):
    _name = 'report_department_balance_department'
    _order = 'code_sufix'

    report_id = fields.Many2one(
        comodel_name='report_trial_balance',
        ondelete='cascade',
        index=True
    )

    department_id = fields.Many2one(
        'account.department',
        index=True
    )

    account_ids = fields.One2many(
        comodel_name='report_trial_balance_account',
        inverse_name='balance_department_id'
    )
    # Data fields, used to keep link with real object
    sequence = fields.Integer(index=True, default=1)
    level = fields.Integer(index=True, default=1)
    name = fields.Char()
    code_sufix = fields.Char()
    currency_id = fields.Many2one('res.currency')
    initial_balance = fields.Float(digits=(16, 2))
    initial_balance_foreign_currency = fields.Float(digits=(16, 2))
    debit = fields.Float(digits=(16, 2))
    credit = fields.Float(digits=(16, 2))
    balance = fields.Float(digits=(16, 2))

    initial_debit = fields.Float(digits=(16, 2))
    initial_credit = fields.Float(digits=(16, 2))
    final_debit = fields.Float(digits=(16, 2))
    final_credit = fields.Float(digits=(16, 2))
    period_balance = fields.Float(digits=(16, 2))
    final_balance = fields.Float(digits=(16, 2))
    final_balance_foreign_currency = fields.Float(digits=(16, 2))


class TrialBalanceReport(models.TransientModel):
    _inherit = 'report_trial_balance'

    by_group_sequence = fields.Boolean('Order by group sequence')
    by_department = fields.Boolean('Department')
    by_month = fields.Boolean('Split by Month')

    parent_id = fields.Many2one(
        comodel_name='report_trial_balance',
        ondelete='cascade',
        index=True
    )
    # Data fields, used to browse report data
    child_ids = fields.One2many(
        comodel_name='report_trial_balance',
        inverse_name='parent_id'
    )
    filter_department_ids = fields.Many2many(comodel_name='account.department')

    department_ids = fields.One2many(
        comodel_name='report_department_balance_department',
        inverse_name='report_id')

    def formatDate(self, dtDateTime,strFormat="%Y-%m-%d"):
        # format a datetime object as YYYY-MM-DD string and return
        return dtDateTime.strftime(strFormat)

    def mkDateTime(self, dateString,strFormat="%Y-%m-%d"):
        # Expects "YYYY-MM-DD" string
        # returns a datetime object
        eSeconds = time.mktime(time.strptime(dateString,strFormat))
        return datetime.datetime.fromtimestamp(eSeconds)

    def mkFirstOfMonth(self, dtDateTime):
        #what is the first day of the current month
        #format the year and month + 01 for the current datetime, then form it back
        #into a datetime object
        return self.mkDateTime(self.formatDate(dtDateTime,"%Y-%m-01"))

    def mkLastOfMonth(self, dtDateTime):
        if int(dtDateTime.strftime("%m"))==12:
            dYear = str(int(dtDateTime.strftime("%Y"))+1)
        else:
            dYear = dtDateTime.strftime("%Y")        #get the year
        dMonth = str(int(dtDateTime.strftime("%m"))%12+1)#get next month, watch rollover
        dDay = "1"                               #first day of next month
        nextMonth = self.mkDateTime("%s-%s-%s"%(dYear,dMonth,dDay))#make a datetime obj for 1st of next month
        delta = datetime.timedelta(seconds=1)    #create a delta of 1 second
        return nextMonth - delta

    def _prepare_report_trial_balance_child(self, start, end):
        self.ensure_one()
        return {
            'date_from': start,
            'date_to': end,
            'only_posted_moves': self.only_posted_moves,
            'hide_account_at_0': self.hide_account_at_0,
            'foreign_currency': self.foreign_currency,
            'company_id': self.company_id.id,
            'filter_account_ids': self.filter_account_ids.ids,
            'filter_partner_ids': self.filter_partner_ids.ids,
            'filter_journal_ids': self.filter_journal_ids.ids,
            'fy_start_date': self.fy_start_date,
            'hierarchy_on': self.hierarchy_on,
            'limit_hierarchy_level': self.limit_hierarchy_level,
            'show_hierarchy_level': self.show_hierarchy_level,
            'hide_parent_hierarchy_level': self.hide_parent_hierarchy_level,
            'show_partner_details': self.show_partner_details,
            'parent_id': self.id
        }

    def get_childs(self):
        _logger.debug('=======GET_CHILDS======')
        start=datetime.datetime.strptime(self.date_from,"%Y-%m-%d")
        end=datetime.datetime.strptime(self.date_to, "%Y-%m-%d")
        _logger.debug('Start Day: %s' % start)
        _logger.debug('End Day: %s' % end)
        months=OrderedDict(((start + timedelta(_)).strftime(r"%m-%y"), None) for _ in xrange((end - start).days)).keys()
        _logger.debug(months)
        for month in months:
            _month=datetime.datetime.strptime(month, "%m-%y")
            first=self.mkFirstOfMonth(_month)
            last=self.mkLastOfMonth(_month)
            if first<start:
                first=start
            if last>end:
                last=end
            _logger.debug('month %s' % _month)
            _logger.debug('First Day: %s' % first)
            _logger.debug('Last Day: %s' % last)
            model = self.env['report_trial_balance']
            report_child = model.create(self._prepare_report_trial_balance_child(first,last))
            report_child.compute_data_for_report()

class TrialBalanceReportCompute(models.TransientModel):
    """ Here, we just define methods.
    For class fields, go more top at this file.
    """
    _inherit = 'report_trial_balance'

    def _compute_group_accounts(self):
        super(TrialBalanceReportCompute, self)._compute_group_accounts()
        query_update_account_params = (self.id,)
        max_lvl_q = """
        SELECT max(level) from report_trial_balance_account where report_id = %s and level is not null
        """
        self.env.cr.execute(max_lvl_q, query_update_account_params)
        max_lvl = self.env.cr.fetchone()[0]
        rtba = self.env['report_trial_balance_account']
        for lvl in range(max_lvl, 0, -1):
            for acc in rtba.search([('level', '=', lvl), ('report_id', '=', self.id)]):
                rtba_id = rtba.search([('account_group_id', '=', acc.parent_id.id), ('report_id', '=', self.id)])
                rtba_id.initial_balance = rtba_id.initial_balance + acc.initial_balance
                rtba_id.final_balance = rtba_id.final_balance + acc.final_balance

    def _update_account_sequence(self):
        super(TrialBalanceReportCompute, self)._update_account_sequence()
        if self.by_group_sequence:
            query_update_account_params = (self.id,)
            query_update_account_group = """
            UPDATE report_trial_balance_account
            SET sequence = 1000000
            WHERE report_trial_balance_account.report_id = %s"""
            self.env.cr.execute(query_update_account_group,
                                query_update_account_params)

            query_update_account_group = """
            UPDATE report_trial_balance_account
            SET sequence = ag.sequence * 1000
            FROM account_group as ag
            WHERE ag.id = report_trial_balance_account.account_group_id
                AND report_trial_balance_account.report_id = %s"""
            self.env.cr.execute(query_update_account_group,
                                query_update_account_params)

    def _set_department_accounts(self, department_ids):
        """Set department values on trial_balance accounts"""
        query_set_department="""
        update report_trial_balance_account
        set balance_department_id=custom.department_id
        from(
        select dept.id as department_id, rag.account_id as account_id, %s as report_id, rag.id as rag_id
        FROM
            report_department_balance_department dept
            inner JOIN report_trial_balance_account AS rag
                ON rag.report_id = %s and dept.report_id =rag.report_id
                and right(rag.code,4)=dept.code_sufix
        ) as custom
        where report_trial_balance_account.id=custom.rag_id
        """
        query_set_department_params = (
            self.id,self.id)
        self.env.cr.execute(query_set_department, query_set_department_params)

    def _inject_department_values(self, department_ids):
        """Inject report values for report_department_balance."""
        query_inject_department= """
            INSERT INTO
                report_department_balance_department
                    (
                    report_id,
                    create_uid,
                    create_date,
                    department_id,
                    name,
                    code_sufix,
                    initial_balance,
                    period_balance,
                    initial_balance_foreign_currency,
                    final_balance,
                    final_balance_foreign_currency
                    )
                SELECT %s AS dreport_id,
                    %s AS dcreate_uid,
                    max(NOW()) AS create_date,
                    dept.id,
                    dept.name,
                    dept.code_sufix,
                    sum(coalesce(rag.initial_balance, 0)) AS initial_balance,
                    sum(coalesce(rag.period_balance, 0)) AS period_balance,
                    sum(coalesce(rag.initial_balance_foreign_currency, 0))
                        AS initial_balance_foreign_currency,
                    sum(coalesce(rag.final_balance, 0)) AS final_balance,
                    sum(coalesce(rag.final_balance_foreign_currency, 0))
                        AS final_balance_foreign_currency
                FROM
                    account_department dept
                    LEFT OUTER JOIN report_trial_balance_account  AS rag
                        ON rag.report_id = %s
                        and right(rag.code,4)=dept.code_sufix
                    where dept.id in %s
                group by dreport_id,dcreate_uid,dept.id,
                    dept.name,dept.code_sufix
                order by dept.code_sufix asc
        """
        query_inject_department_params = (
            self.id,
            self.env.uid,
            self.id,
            department_ids._ids
        )
        self.env.cr.execute(query_inject_department, query_inject_department_params)

    @api.multi
    def compute_data_for_report(self):
        super(TrialBalanceReportCompute, self).compute_data_for_report()
        #if childs??
        if self.by_month and  not self.parent_id:
            self.get_childs()
        if self.by_department:
            if self.filter_department_ids:
                department_ids = self.filter_department_ids
            else:
                department_ids = self.env['account.department'].search(
                    [('company_id', '=', self.company_id.id)])
            self._inject_department_values(department_ids)
            self._set_department_accounts(department_ids)

    def _get_html(self):
        result = {}
        rcontext = {}
        context = dict(self.env.context)
        report = self.browse(context.get('active_id'))
        if report:
            rcontext['o'] = report
            if report.by_department:
                result['html'] = self.env.ref('account_financial_report_extension.report_department_balance').render(
                    rcontext)
            elif report.by_month and report.hierarchy_on != 'none':
                result['html'] = self.env.ref('account_financial_report_extension.report_trial_balance_by_month').render(
                    rcontext)
            else:
                result=super(TrialBalanceReportCompute, self)._get_html()
        return result

    def write_month_line(self, child, line_object):
        """Write a line on current line using all defined columns field name."""
        month_account=self.env['report_trial_balance_account'].search([
            ('report_id','=',child.id),
            ('account_group_id','=',line_object.account_group_id.id),])

        value = month_account.final_balance-month_account.initial_balance
        value = round(value, 2)
        return value
    
    def _get_root_parent(self, account):
        if account.parent_id:
            res=self._get_root_parent(account.parent_id)
        else:
            res=account
        return res

    def _get_group_account(self, account_ids):
        groups = []
        for account in account_ids.filtered(lambda a: not a.hide_line):
            account_group = self._get_root_parent(account.account_group_id)
            if not account_group in groups:
                groups.append(account_group)
        return groups

    def _get_accounts_details(self, group, account_ids):
        accounts = []
        for account in account_ids.filtered(lambda a: not a.hide_line):
            account_group = self._get_root_parent(account.account_group_id)
            if account_group.id == group.id:
                accounts.append(account)
        return accounts
    
    def _get_format_date_header(self, child_date):
        """Date format in xml"""
        month=datetime.datetime.strptime(child_date,"%Y-%m-%d")
        month=month.strftime("%b-%Y")
        return month

    def write_month_line_sumas_saldos(self, child, line_object):
        """Write a line on current line using all defined columns field name."""
        month_account=self.env['report_trial_balance_account'].search([
            ('report_id','=',child.id),
            ('account_id','=',line_object.account_id.id),])

        value = month_account.period_balance
        value = round(value, 2)
        return value

    @api.multi
    def print_report(self, report_type):
        self.ensure_one()
        context = dict(self.env.context)
        report = self.browse(context.get('active_id'))
        if report:
            if report.by_month and report_type != 'xlsx' and report.hierarchy_on != 'none':
                report_type = 'months'
            elif report.by_department and report_type != 'xlsx' and report.hierarchy_on != 'none':
                report_type = 'department'

        if report_type == 'xlsx':
            report_name = 'a_f_r.report_trial_balance_xlsx'
        # TEMPLATE FOR SPLIT BY MONTH
        elif report_type == 'months':
            report_name = 'account_financial_report_extension.' \
                          'report_trial_balance_by_month_qweb'
            report_type = 'qweb-pdf'
        # TEMPLATE FOR BY DEPARTMENT 
        elif report_type == 'department':
            report_name = 'account_financial_report_extension.' \
                          'report_department_balance_qweb'
            report_type = 'qweb-pdf'
        else:
            report_name = 'account_financial_report.' \
                          'report_trial_balance_qweb'
        return self.env['ir.actions.report'].search(
            [('report_name', '=', report_name),
             ('report_type', '=', report_type)], limit=1).report_action(self)

class TrialBalanceReportAccount(models.TransientModel):
    _inherit = 'report_trial_balance_account'

    balance_department_id = fields.Many2one(
        comodel_name='report_department_balance_department',
        ondelete='cascade',
        index=True
    )

    account_group_code_prefix = fields.Char(related="parent_id.code_prefix")
    account_gruop_name = fields.Char(related="parent_id.name")

    def _compute_hide_line(self):
        for rec in self:
            report = rec.report_id
            r = (rec.currency_id or report.company_id.currency_id).rounding
            if report.by_group_sequence:
                if (rec.account_group_id):
                    if (report.hide_account_at_0 and (
                    float_is_zero(rec.initial_balance, precision_rounding=r)
                    and float_is_zero(rec.final_balance, precision_rounding=r)
                    and float_is_zero(rec.debit, precision_rounding=r)
                    and float_is_zero(rec.credit, precision_rounding=r))):
                        rec.hide_line = True
                    else:
                        rec.hide_line = False
                else:
                    rec.hide_line = True
            else:
                super(TrialBalanceReportAccount,self)._compute_hide_line()
