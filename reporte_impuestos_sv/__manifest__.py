# -*- coding: utf-8 -*-
{
	'name': 'Reporte de Iva Para El Salvador',
	'version': '1.0',
	'category': 'Accounting',
	'description': '''\ Este modulo crea lo necesario para generar un reporte impreso del libro de iva 
				y poder generar el de compra y ventas''',
	'author': 'Delfos Cloud (Jose Francisco Trejo Rivera)',
	'website': 'http://www.delfos-cloud.com',
	'price': 250.00,
	'currency': 'USD',
	'license': 'AGPL-3',
	'data': [
		'report/libro_iva_fcf.xml',
		'report/libro_iva_ccf.xml',
		'report/libro_iva_compras.xml',
		'report/report_libro_iva.xml',
		'report/libro_iva.xml',
		'views/libro_iva_view.xml',
		'views/wizard_tax_adjustments.xml',
		'security/ir.model.access.csv',
		'security/iva_security.xml',
			],
	'depends': [
		'base',
		'account',
		'l10n_invoice_sv',
		],
	'installable': True,
	'auto_install': False,
	'post_init_hook': 'drop_print',
}
