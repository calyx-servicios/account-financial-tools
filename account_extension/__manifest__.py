# -*- coding: utf-8 -*-
{
    'name': "Account Extension",

    'summary': """
       Modifications and adaptations on account models.\n
       - The Draft Button of Invoices won't assign blank (False) to the Account Date.
       - Account Payment Group tree view add Payment Currency, Currency Rate and Withholding Summary.
        """,

    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Tools',
    'version': '11.0.1.2.0',

    # any module necessary for this one to work correctly
    'depends': [
        'account',
        'account_payment_group',
        'account_withholding',
        'l10n_ar_account',
        'manual_currency_exchange_rate',
        'sale'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/res_partner_id_category_data.xml',
        'views/account_invoice_view.xml',
        'views/account_payment_view.xml',
        'views/account_payment_group_assets.xml',
        "report/invoice_analysis.xml"
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
