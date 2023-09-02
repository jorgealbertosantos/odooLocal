# -* coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
  _inherit = 'res.config.settings'

  invoice_line_number = fields.Integer(string='# de lineas por factura',
                                       help="No. de lineas que poseen las facturas en general")

  p_u_partner = fields.Boolean(string="Ver pagos de socio titular en factura",
                               help="Habilitando este opcion solo puede ver en factura los pagos del socio titular de la factura")

  @api.model
  def get_values(self):
    res = super(ResConfigSettings, self).get_values()
    conf = self.env['ir.config_parameter']
    iln = int(conf.get_param('invoice_sv.invoice_line_number'))
    pup = conf.get_param('invoice_sv.payment_unique_partner')
    res.update(invoice_line_number=iln)
    res.update(p_u_partner=pup)
    return res

  @api.one
  def set_values(self):
    super(ResConfigSettings, self).set_values()
    conf = self.env['ir.config_parameter']
    conf.set_param('invoice_sv.invoice_line_number',
                   str(self.invoice_line_number))
    conf.set_param('invoice_sv.payment_unique_partner',
                   str(self.p_u_partner))
    