# -*- coding: utf-8 -*-
{
    'name': "Localizacion Base de El Salvador",
    'summary': """Localizacion Base de El Salvador""",
    'description': """
    Localizacion de El Salvador :
        - Documento de Identificacion Unico
        """,
    'author': "Intelitecsa(Francisco Trejo)",
    'website': "http://www.intelitecsa.com",
    "images": ['static/description/banner.png',
               'static/description/icon.png',
               'static/description/thumbnail.png'],
    'price': 30.00,
    'currency': 'USD',
    'license': 'GPL-3',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization',
    'version': '1.1',
    # any module necessary for this one to work correctly
    'depends': ['base'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/res_lang.xml',
        'views/view_res_partner.xml',
        'views/view_res_company.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/res_company_demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
