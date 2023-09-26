from odoo import fields, models, api


class AccountType(models.Model):
    _inherit = 'account.account.type'


    internal_group = fields.Selection(selection_add=[('cost', 'Costo')])
