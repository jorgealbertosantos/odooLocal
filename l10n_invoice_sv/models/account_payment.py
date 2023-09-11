# -*- coding: utf-8 -*-

from odoo import models, _, exceptions


class AccountPayment(models.Model):
  _inherit = "account.payment"

  def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
    conf = self.env['ir.config_parameter']
    pup = conf.get_param('invoice_sv.payment_unique_partner')
    #print(pup,'***********************')
    if pup:
      # pylint: disable=E1101
      partner_id = self.partner_id.id
    else:
      # pylint: disable=E1101
      # pylint: disable=W0212
      partner_id = self.env['res.partner']._find_accounting_partner(self.partner_id).id

    return {
        'partner_id': partner_id or False,
        'invoice_id': invoice_id and invoice_id.id or False,
        'move_id': move_id,
        'debit': debit,
        'credit': credit,
        'amount_currency': amount_currency or False,
        'payment_id': self.id,
        'journal_id': self.journal_id.id,
    }
