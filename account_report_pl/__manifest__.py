# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "P&L Report",
    "summary": """
        This module allows to group accounts by concepts and then
        show their totals in a report
        """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["Paradiso Cristian"],
    "website": "http://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Account",
    "version": "11.0.1.0.0",
    "application": False,
    "installable": True,
    "depends": ['account',
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/report_pl_views.xml",
        "views/account_view.xml",
    ],
}
