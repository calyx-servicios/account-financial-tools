# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from datetime import  timedelta
import time
import datetime
from collections import OrderedDict
import logging
_logger = logging.getLogger(__name__)

class GeneralLedgerReport(models.TransientModel):
    _inherit = "report_general_ledger"
    show_ungroup = fields.Boolean()


class GeneralLedgerReportCompute(models.TransientModel):

    _inherit = 'report_general_ledger'

    def _get_html(self):
        result = {}
        rcontext = {}
        context = dict(self.env.context)
        report = self.browse(context.get('active_id'))
        if report:
            rcontext['o'] = report
            if report.show_ungroup:
                result['html'] = self.env.ref(
                    'account_general_ledger_customization.report_general_ledger_customization').render(
                    rcontext)
            else:
                result=super(GeneralLedgerReportCompute, self)._get_html()
        return result

    @api.multi
    def compute_data_for_report(self,with_line_details=True,with_partners=True):
        super(GeneralLedgerReportCompute, self).compute_data_for_report(with_line_details, with_partners)
        if self.show_ungroup:
            query_update_display_name = """
            UPDATE
                report_general_ledger_move_line
            SET
                entry_name = custom_values.display_name,
                account_name=custom_values.account_name
            FROM
                (
                    (SELECT
                        rml.id AS line_id,
                        ra.name as account_name,
                        a.display_name as display_name
                    FROM
                        account_move_line ml
                    INNER JOIN
                        report_general_ledger_move_line rml
                            ON ml.id = rml.move_line_id
                    INNER JOIN
                        report_general_ledger_account ra
                            ON rml.report_account_id = ra.id
                    INNER JOIN
                        account_move a
                            on ml.move_id=a.id
                    WHERE
                        ra.report_id = %(report_id)s)
                UNION
                    (SELECT
                        rml.id AS line_id,
                        ra.name as account_name,
                        a.display_name as display_name
                    FROM
                        account_move_line ml
                    INNER JOIN
                        report_general_ledger_move_line rml
                            ON ml.id = rml.move_line_id
                    INNER JOIN
                        report_general_ledger_partner rp
                            ON rml.report_partner_id = rp.id
                    INNER JOIN
                        report_general_ledger_account ra
                            ON rp.report_account_id = ra.id
                    INNER JOIN
                        account_move a
                            on ml.move_id=a.id
                    WHERE
                        ra.report_id = %(report_id)s
                    )
                ) AS custom_values
            WHERE
                report_general_ledger_move_line.id = custom_values.line_id
                        """
            params = {
                'report_id': self.id,
            }
            self.env.cr.execute(query_update_display_name, params)

        query_update_center_name = """
            UPDATE
                report_general_ledger_move_line
            SET
                center_name=custom_values.center_name
            FROM
                (
                    SELECT
                        rml.id AS line_id,
                        concat(aa.code,' ',aa.name) as center_name
                    FROM
                        account_move_line ml
                    INNER JOIN
                        report_general_ledger_move_line rml
                            ON ml.id = rml.move_line_id
                    INNER JOIN
                        report_general_ledger_account ra
                            ON rml.report_account_id = ra.id
                    INNER JOIN
                        account_analytic_account aa
                            ON
                            ml.analytic_account_id = aa.id
                    WHERE
                        ra.report_id = %(report_id)s
                ) AS custom_values
            WHERE
                report_general_ledger_move_line.id = custom_values.line_id
            """
        params = {
                'report_id': self.id,
            }
        self.env.cr.execute(query_update_center_name, params)

class GeneralLedgerReportMoveLine(models.TransientModel):
    _inherit = 'report_general_ledger_move_line'

    entry_name = fields.Char()
    account_name = fields.Char()
    center_name = fields.Char()
