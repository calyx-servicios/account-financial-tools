# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Asset Sap Fields",
    "summary": """
        Create a fields for SAP template importation.""",
    "author": "Calyx Servicios S.A.",
    "maintainers": ["JhoneM"],
    "website": "http://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Accounting/Accounting",
    "version": "13.0.1.0.0",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": ["account_asset_management"],
    "data": ["views/account_asset_view.xml"],
}
