# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions
class Partner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'phone.validation.mixin']
    #Datos Personales
    dui = fields.Char(string="D.U.I.")
    nit = fields.Char(string="N.I.T.")
    nrc = fields.Char(string="N.R.C.")
    giro = fields.Char(string="Giro")
    #Datos de contacto
    fax = fields.Char(string="Fax")
    pbx = fields.Char(string="PBX")
    extension = fields.Char(string="Extension")
    directo = fields.Char(string="Directo")
    
    @api.onchange('pbx', 'fax', 'country_id', 'company_id')
    def _onchange_phone_validation(self):
        if self.pbx:
            self.pbx = self.phone_format(self.pbx)
        if self.fax:
            self.fax = self.phone_format(self.fax)
            

    
    