# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions
class Partner(models.Model):
    _inherit = 'res.partner'
    #Datos Personales
    dui = fields.Char(string="D.U.I.")
    vat = fields.Char(string="N.I.T.")
