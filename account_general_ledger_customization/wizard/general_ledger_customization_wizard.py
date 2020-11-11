# Author: Julien Coux
# Copyright 2016 Camptocamp SA
# Copyright 2017 Akretion - Alexis de Lattre
# Copyright 2018 Eficent Business and IT Consuting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pycompat
from odoo.exceptions import UserError, ValidationError


class GeneralLedgerReportCustomizationWizard(models.TransientModel):

	_inherit = "general.ledger.report.wizard"
	ungroup = fields.Boolean('Ungroup')

	def _prepare_report_general_ledger(self):
		self.ensure_one()
		ret = super(GeneralLedgerReportCustomizationWizard, self)._prepare_report_general_ledger()
		ret.update({'show_ungroup': self.ungroup}) 
		return ret