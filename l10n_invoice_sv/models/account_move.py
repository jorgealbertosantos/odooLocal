# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from .amount_to_text_sv import to_word

class AccountMove(models.Model):
  _inherit = 'account.move'

  inv_refund_id = fields.Many2one('account.move',
                                  'Factura Relacionada',
                                  copy=False,
                                  track_visibility='onchange')

  state_refund = fields.Selection([
          ('refund', 'Retificada'),
          ('no_refund', 'No Retificada'),
      ],
    string="Retificada",
    index=True,
    readonly=True,
    default='no_refund',
    track_visibility='onchange',
    copy=False)

  amount_text = fields.Char(string=_('Amount to text'),
                            store=True,
                            readonly=True,
                            compute='_amount_to_text',
                            track_visibility='onchange')

  @api.depends('amount_total')
  def _amount_to_text(self):
    for l in self:
      l.amount_text = to_word(l.amount_total)



  def action_invoice_print(self):
    """ Print the invoice and mark it as sent, so that we can see more
        easily the next step of the workflow
    """
    if any(not move.is_invoice(include_receipts=True) for move in self):
      raise UserError(_("Solo se pueden imprimir facturas."))

    self.filtered(lambda inv: not inv.invoice_sent).write({'invoice_sent': True})

    report = self.journal_id.type_report

    if report == 'ccf':
      return self.env.ref('l10n_invoice_sv.report_credito_fiscal').report_action(self)
    if report == 'fcf':
      return self.env.ref('account.account_invoices').report_action(self)
    if report == 'exp':
      return self.env.ref('l10n_invoice_sv.report_exportacion').report_action(self)
    if report == 'ndc':
      return self.env.ref('l10n_invoice_sv.report_ndc').report_action(self)
    if report == 'anu':
      return self.env.ref('account.account_invoice_action_report_duplicate').report_action(self)
    if report == 'axp':
      return self.env.ref('l10n_invoice_sv.report_anul_export').report_action(self)

    return self.env.ref('account.account_invoices').report_action(self)

  def msg_error(self, campo):
    raise ValidationError("No puede emitir un documento si falta un campo Legal "\
                                     "Verifique %s" % campo)

  def action_post(self):
    '''validamos que partner cumple los requisitos basados en el tipo
    de documento de la sequencia del diario selecionado'''

    #si es factura normal'
    if self.type != 'entry':
      type_report = self.journal_id.type_report

      if type_report == 'ccf':
        if not self.partner_id.parent_id:
          if not self.partner_id.nrc:
            self.msg_error("N.R.C.")
          if not self.partner_id.vat:
            self.msg_error("N.I.T.")
          if not self.partner_id.giro:
            self.msg_error("Giro")
        else:
          if not self.partner_id.parent_id.nrc:
            self.msg_error("N.R.C.")
          if not self.partner_id.parent_id.vat:
            self.msg_error("N.I.T.")
          if not self.partner_id.parent_id.giro:
            self.msg_error("Giro")

      if type_report == 'fcf':
        if not self.partner_id.parent_id:
          if not self.partner_id.vat:
            self.msg_error("N.I.T.")
          if self.partner_id.company_type == 'person':
            if not self.partner_id.dui:
              self.msg_error("D.U.I.")
        else:
          if not self.partner_id.parent_id.vat:
            self.msg_error("N.I.T.")
          if self.partner_id.parent_id.company_type == 'person':
            if not self.partner_id.dui:
              self.msg_error("D.U.I.")

      if type_report == 'exp':
        for l in self.invoice_line_ids:
          if not l.product_id.arancel_id:
            self.msg_error("Posicion Arancelaria del Producto %s" %l.product_id.name)

      #si es retificativa
      if type_report == 'ndc':
        if not self.partner_id.parent_id:
          if not self.partner_id.nrc:
            self.msg_error("N.R.C.")
          if not self.partner_id.vat:
            self.msg_error("N.I.T.")
          if not self.partner_id.giro:
            self.msg_error("Giro")
        else:
          if not self.partner_id.parent_id.nrc:
            self.msg_error("N.R.C.")
          if not self.partner_id.parent_id.vat:
            self.msg_error("N.I.T.")
          if not self.partner_id.parent_id.giro:
            self.msg_error("Giro")

    return super(AccountMove, self).action_post()
