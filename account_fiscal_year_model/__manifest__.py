# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Account Fiscal Year Model',
    'summary': """
        This module adds the Account Fiscal Year Model. It was migrated to EE.""",

    'author': 'Calyx Servicios S.A.',
    'maintainers': ['FedericoGregori'],

    'website': 'http://www.calyxservicios.com.ar/',
    'license': 'AGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '11.0.1.0.0',
    # see https://odoo-community.org/page/development-status
    'development_status': 'Production/Stable',

    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account'
        ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_fiscal_year_view.xml'
    ],

    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
