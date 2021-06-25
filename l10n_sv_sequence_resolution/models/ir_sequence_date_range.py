# -*- coding: utf-8 -*-
# Copyright 2021 Alejandro Olano <Github@alejo-code>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrSequenceDateRange(models.Model):
    _inherit = 'ir.sequence.date_range'

    use_dgii_control = fields.Boolean(string='Use DGII Resolutions Control?',
                                      related='sequence_id.use_dgii_control',
                                      store=False)
    prefix = fields.Char(string='Prefix')
    resolution_number = fields.Char(string='Resolution Number')
    number_from = fields.Integer(string='Initial Number',
                                 default=False,
                                 size=100)
    number_to = fields.Integer(string='Final Number', default=False)
    serial_document = fields.Char(string='Serial Document')
    active_resolution = fields.Boolean(string='Active Resolution?')
