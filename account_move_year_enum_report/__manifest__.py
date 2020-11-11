# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Move Fiscal Year Pdf Report",
    "summary": """
        Report PDF for account move Fiscal Year""",
    "author": "Calyx Servicios S.A.",
    "maintainers": ["Lolstalgia"],
    "website": "http://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    "category": "Technical Settings",
    "version": "11.0.1.0.0",
    # see https://odoo-community.org/page/development-status
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    # any module necessary for this one to work correctly
    "depends": ["base", "account", "account_move_year_enum"],
    # always loaded
    "data": [
        "report/account_move_fy_report_action.xml",
        "report/account_move_fy_report_template.xml",
        "wizard/account_move_fy_wizard.xml",
    ],
}
