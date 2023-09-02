# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions
class Company(models.Model):
    _inherit = 'res.company'
    
    nrc = fields.Char(string="N.R.C.")
    nit = fields.Char(string="N.I.T.")
    giro = fields.Char(string="Giro")
    #Datos de contacto
    fax = fields.Char(string="Fax")
    pbx = fields.Char(string="PBX")
        
    @api.onchange('nrc','nit','giro','pbx','fax','country_id')
    def _change_data_fiscal(self):
        self.partner_id.write({
            'nrc': self.nrc,
            'nit': self.nit,
            'giro': self.giro,
            'pbx': self.pbx,
            'fax': self.fax})        
