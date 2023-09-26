    # -*- coding: utf-8 -*-
{
    'name': "Localizacion de El Salvador",
    'summary': """Localizacion de El Salvador""",
    'description': """
    Localizacion de El Salvador :
        - Numero de registro comercial
        - Numero de identificacion tributario
        - Documento de Identificacion Unico
        
    Agrega un plan contable basico requerido en El Salvador.
    Agrega categorias de impuestos utilizados en El Salvador.
    Agrega todos los impuestos utilizados en compras y ventas.
    
    Permite generar los tres tipos de facturas utilizados en El Salvador
        - Consumidor Final.
        - Credito Fiscal.
        - Exportaciones.
    
    Tambien permite generar los documentos que retifican:
        - Anulaciones.
        - Nota de Credito.
        - Anulaciones de Exportacion.
        """,
    'author': "Intelitecsa(Francisco Trejo)",
    'website': "http://www.intelitecsa.com",
    "images": ['static/description/banner.png',
               'static/description/icon.png',
               'static/description/thumbnail.png'],
    'price': 100.00,
    'currency': 'USD',
    'license': 'GPL-3',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization',
    'version': '1.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'phone_validation'],
    # always loaded
    'data': [
        'views/view_res_company.xml',
        'views/view_res_partner.xml',
        'data/l10n_sv_coa_chart_data.xml',
        'data/account_tax_data.xml',
        'data/sequence_data.xml',
        'data/journal_data.xml',
        'data/account_fiscal_position.xml',
        'data/account_fiscal_position_tax.xml',
        'data/account_chart_template_data.xml',
        'data/res_country_data.xml',
        'views/account_type.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    #'post_init_hook': 'drop_journal',
}
