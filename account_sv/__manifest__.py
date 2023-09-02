# -*- coding: utf-8 -*-
{
    'name': "Reportes de Contabilidad Genericos Diarios",

    'summary': """
        Permite generear Reportes de Contabilidad Genericos Diarios
        """,

    'description': """
        Reportes de Contabilidad Genericos Diarios
        
        * Permite generar el libro diario mayor.
        * Permite generar el libro mayor.
    """,
    'author': "Intelitecsa (Francisco Trejo)",
    'website': "https://www.intelictesa.com",
    'category': 'Sales',
    'price': 100.00,
    'currency': 'USD',
    'license': 'AGPL-3',
    'version': '1.3',
    'depends': [
        'base',
        'mail',
        'account',
        'account_accountant',
        'account_reports',
        ],
    'data': [
      'views/account_views.xml',
      'security/ir.model.access.csv',
      'wizards/wizard_account_char_view.xml',
      'report/template_account_chart.xml',
      'report/chart_accounts.xml',
      'wizards/wizard_journal_mayor_view.xml',
      'report/journal_mayor_report.xml',
      'report/journal_mayor_template.xml',
    ],
    'demo': [
        'data/accounts.xml',
        #'demo/demo.xml',
    ],
}
