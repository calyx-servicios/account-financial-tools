# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Financial Report Usd Amount",
    "summary": """
        Adds a initial balance in USD to report trial balance.\n
        Compute the amounts in USD based in exchange rate.""",
    "author": "Calyx Servicios S.A.",
    "maintainers": ["JhoneM"],
    "website": "http://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Technical Settings",
    "version": "11.0.1.0.2",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": [
        "account",
        "account_financial_report",
        "web_notify",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/report_trial_balance_initial_amount.xml",
        "wizard/trial_balance_wizard.xml",
    ],
}
