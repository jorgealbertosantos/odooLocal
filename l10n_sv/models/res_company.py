# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions
class Company(models.Model):
    _inherit = 'res.company'
    
    company_registry = fields.Char(string="N.R.C.")
    vat = fields.Char(string="N.I.T.")
    giro = fields.Char(string="Giro")
    #Datos de contacto
    fax = fields.Char(string="Fax")
    pbx = fields.Char(string="PBX")
        
    @api.onchange('nrc')
    def change_nrc(self):
        self.partner_id.nrc = self.nrc         

    @api.onchange('vat')
    def change_nrc(self):
        self.partner_id.vat = self.vat
        
    @api.onchange('giro')
    def change_nrc(self):
        self.partner_id.giro = self.giro
          
    @api.onchange('pbx')
    def change_nrc(self):
        self.partner_id.nrc = self.pbx
        
    @api.onchange('fax')
    def change_nrc(self):
        self.partner_id.fax = self.fax