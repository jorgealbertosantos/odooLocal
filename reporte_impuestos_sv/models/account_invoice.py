# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class account_invoice(models.Model):
        _name = "account.invoice"
        _inherit = "account.invoice"
        active = fields.Boolean('Libro Iva' , help='- Estara activo si esta factura ya fue contabilizada en el libro de iva'  , default=True,)
        
account_invoice()
