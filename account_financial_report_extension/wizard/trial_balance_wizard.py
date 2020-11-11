# Author: Julien Coux
# Copyright 2016 Camptocamp SA
# Copyright 2017 Akretion - Alexis de Lattre
# Copyright 2018 Eficent Business and IT Consuting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pycompat
from odoo.exceptions import UserError, ValidationError


class TrialBalanceReportWizard(models.TransientModel):


	_inherit = "trial.balance.report.wizard"

	by_group_sequence = fields.Boolean('Order by group sequence')
	by_department = fields.Boolean('By Department')
	by_month = fields.Boolean('Split by Month')

	department_ids = fields.Many2many(
        comodel_name='account.department',
        string='Filter departments',
    	)



	def _prepare_report_trial_balance(self):
		self.ensure_one()
		ret = super(TrialBalanceReportWizard, self)._prepare_report_trial_balance()
		ret.update({
			'by_group_sequence': self.by_group_sequence,
			'by_department': self.by_department,
			'by_month': self.by_month,
			})
		if self.department_ids:
			ret.update({
				'filter_department_ids': [(6, 0, self.department_ids.ids)],
			})
		return ret
	
	def _export(self, report_type):
		"""Default export is PDF."""
		model = self.env['report_trial_balance']
		report = model.create(self._prepare_report_trial_balance())
		if report.by_month and report_type != 'xlsx' and report.hierarchy_on != 'none':
			report_type = 'months'
		elif report.by_department and report_type != 'xlsx' and report.hierarchy_on != 'none':
			report_type = 'department'
		report.compute_data_for_report()
		return report.print_report(report_type)