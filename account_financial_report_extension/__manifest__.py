# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Finacial Report Extension',
    'version': '11.0.0',
    'category': 'Tools',
    'summary': ' ',
    'author': "Calyx",
    'website': 'www.calyxservicios.com.ar',
    'license': 'AGPL-3',
    'depends': [
                'account','account_financial_report',
            ],
    'data': [
            'view/group_view.xml',
            'view/department_view.xml',
            'reports.xml',
            'wizard/trial_balance_wizard.xml',
            'report/department_balance.xml',
            'security/ir.model.access.csv',
            ],
    'installable': True,
    'application': False,
}
