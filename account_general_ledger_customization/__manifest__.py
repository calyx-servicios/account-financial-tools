# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Financial General Ledger Report Customization',
    'version': '11.0.0',
    'category': 'Tools',
    'summary': ' ',
    'author': "Calyx",
    'website': 'www.calyxservicios.com.ar',
    'license': 'AGPL-3',
    'depends': [
                'account_financial_report',
            ],
    'data': [
            'view/ungroup_view.xml',
            'report/templates/general_ledger.xml',
            ],
    'installable': True,
    'application': False,
}
