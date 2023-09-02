# -*- coding: utf-8 -*-
# Copyright 2021 Alejandro Olano <Github@alejo-code>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = "account.journal"

    class_document = fields.Selection(selection=[
        ('1', 'PRINTED BY PRINTER OR TICKETS'), ('2', 'SINGLE FORM')
    ],
                                      string='Class Document')
    type_document = fields.Selection(selection=[(
        '01', 'FINAL CONSUMER INVOICE'
    ), ('02', 'SIMPLIFIED SALES INVOICE'), (
        '03', 'Tax Credit Voucher'), ('05', 'Credit Note'), (
            '06',
            'Debit Note'), ('10',
                            'REGISTER MACHINE TICKETS'), ('11',
                                                          'EXPORT BILL')])
