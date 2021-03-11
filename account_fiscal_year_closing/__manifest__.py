# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Fiscal Year Closing",
    "summary": """
        This module adds the function to make \
            the account closing for a fiscal year.""",
    "author": "Calyx Servicios S.A.",
    "maintainers": ["JhoneM"],
    "website": "http://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Technical Settings",
    "version": "11.0.1.2.3",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": [
        "account",
        "account_fiscal_year_backported",
        "web_notify",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/account_account_type.xml",
        "views/account_account.xml",
        "views/account_journal.xml",
        "wizard/fiscal_year_closing.xml",
    ],
}
