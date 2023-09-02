# -*- coding: utf-8 -*-
# Copyright 2021 Alejandro Olano <Github@alejo-code>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    use_dgii_control = fields.Boolean(string='Use DGII Resolutions Control?')
    remaining_numbers = fields.Integer(string='Remaining Numbers',
                                       default=False)
    remaining_days = fields.Integer(string='Remaining Days', default=False)
    internal_number_from = fields.Integer(
        string='Internal Control Initial Number',
        default=False,
        size=100,
        compute="_internal_control",
        store=True)
    internal_number_to = fields.Integer(string='Internal Control Final Number',
                                        default=False,
                                        size=100,
                                        compute="_internal_control",
                                        store=True)

    @api.multi
    def _internal_control(self):
        for record in self:
            jounal_clas = self.env["account.journal"].search([
                ('sequence_id', '=', record.id)
            ])
            for journal in jounal_clas:
                if journal.class_document == '1':
                    record.internal_number_from = record.date_range_ids.number_from
                    record.internal_number_to = record.date_range_ids.number_to

    @api.onchange('use_dgii_control')
    def onchange_active_resolution(self):
        for sequence_id in self:
            sequence_id.use_date_range = True
