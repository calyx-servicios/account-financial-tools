# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Account Move Year Enum',
    'summary': """
        Every account move will get it's own numeration based on the year.""",

    'author': 'Calyx Servicios S.A., Odoo Community Association (OCA)',
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
        'account',
        'account_fiscal_year_backported',
        'report_xlsx'
        ],

    # always loaded
    'data': [
        'views/account_move_views.xml',
        'wizard/account_move_enum_wizard.xml',
        'wizard/account_move_fy_wizard.xml',
        'reports/account_move_fy_report_action.xml'
    ],

    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
