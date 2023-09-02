# -*- coding: utf-8 -*-
import json
from odoo.tools import float_is_zero
from .amount_to_text_sv import to_word
from odoo import api, fields, models, _, exceptions

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    inv_refund_id = fields.Many2one('account.invoice','Factura Relacionada', copy=False, track_visibility='onchange')

    state_refund = fields.Selection([
            ('refund','Retificada'),
            ('no_refund','No Retificada'),
        ], string="Retificada", index=True, readonly=True, default='no_refund',
        track_visibility='onchange', copy=False)
    
    amount_text = fields.Char(string=_('Amount to text'), store=True, readonly=True,
                              compute='_amount_to_text', track_visibility='onchange')
       
    @api.one
    @api.depends('amount_total')
    def _amount_to_text(self):
        self.amount_text = to_word(self.amount_total)

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
      conf = self.env['ir.config_parameter']
      iln = int(conf.get_param('invoice_sv.invoice_line_number'))
      ivl = len(self.invoice_line_ids)
      if self.type in ['out_invoice','out_refund']:
        if ivl > iln:
          raise exceptions.ValidationError("No puede Crear facturas con %s lineas"\
                    "el maximo permitido es %s" % (ivl,iln))
      for l in self.invoice_line_ids:
        if len(l.invoice_line_tax_ids) > 1:
          raise exceptions.ValidationError("No puede Crear lineas de facturas con %s impuestos."\
                    "Solo puede colocar un impuesto por producto revisar %s" % (len(l.invoice_line_tax_ids),l.display_name))
    
    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        
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
    
    @api.multi
    def msg_error(self,campo):
      raise exceptions.ValidationError("No puede emitir un documento si falta un campo Legal "\
                                       "Verifique %s" % campo)
      return True
    
    @api.multi
    def action_invoice_open(self):
        '''validamos que partner cumple los requisitos basados en el tipo
        de documento de la sequencia del diario selecionado'''
        inv_type = self.type
        #si es factura normal
        type_report = self.journal_id.type_report
    
        if type_report == 'ccf':
          if not self.partner_id.parent_id:
            if not self.partner_id.nrc:
              self.msg_error("N.R.C.")
            if not self.partner_id.nit:
              self.msg_error("N.I.T.")
            if not self.partner_id.giro:
              self.msg_error("Giro")
          else:
            if not self.partner_id.parent_id.nrc:
              self.msg_error("N.R.C.")
            if not self.partner_id.parent_id.nit:
              self.msg_error("N.I.T.")
            if not self.partner_id.parent_id.giro:
              self.msg_error("Giro")
    
        if type_report == 'fcf':
          if not self.partner_id.parent_id:          
            if not self.partner_id.nit:
              self.msg_error("N.I.T.")
            if self.partner_id.company_type == 'person':
              if not self.partner_id.dui:
                self.msg_error("D.U.I.")
          else:
            if not self.partner_id.parent_id.nit:
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
            if not self.partner_id.nit:
              self.msg_error("N.I.T.")
            if not self.partner_id.giro:
              self.msg_error("Giro")
          else:
            if not self.partner_id.parent_id.nrc:
              self.msg_error("N.R.C.")
            if not self.partner_id.parent_id.nit:
              self.msg_error("N.I.T.")
            if not self.partner_id.parent_id.giro:
              self.msg_error("Giro")
              
        return super(AccountInvoice, self).action_invoice_open()

    @api.one
    def _get_outstanding_info_JSON(self):
        self.outstanding_credits_debits_widget = json.dumps(False)
        if self.state == 'open':
            conf = self.env['ir.config_parameter']
            pup = conf.get_param('invoice_sv.payment_unique_partner')
            #print(pup,'***********************')
            if pup:
              partner_id = self.partner_id.id
            else:
              partner_id = self.env['res.partner']._find_accounting_partner(self.partner_id).id
            # print(self.env['res.partner']._find_accounting_partner(self.partner_id).id)
            # print(partner_id)
            domain = [('account_id', '=', self.account_id.id),
                      ('partner_id', '=', partner_id),
                      ('reconciled', '=', False),
                      '|',
                        '&', ('amount_residual_currency', '!=', 0.0), ('currency_id','!=', None),
                        '&', ('amount_residual_currency', '=', 0.0), '&', ('currency_id','=', None), ('amount_residual', '!=', 0.0)]
            if self.type in ('out_invoice', 'in_refund'):
                domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                type_payment = _('Outstanding credits')
            else:
                domain.extend([('credit', '=', 0), ('debit', '>', 0)])
                type_payment = _('Outstanding debits')
            info = {'title': '', 'outstanding': True, 'content': [], 'invoice_id': self.id}
            lines = self.env['account.move.line'].search(domain)
            currency_id = self.currency_id
            if len(lines) != 0:
                for line in lines:
                    # get the outstanding residual value in invoice currency
                    if line.currency_id and line.currency_id == self.currency_id:
                        amount_to_show = abs(line.amount_residual_currency)
                    else:
                        amount_to_show = line.company_id.currency_id.with_context(date=line.date).compute(abs(line.amount_residual), self.currency_id)
                    if float_is_zero(amount_to_show, precision_rounding=self.currency_id.rounding):
                        continue
                    if line.ref :
                        title = '%s : %s' % (line.move_id.name, line.ref)
                    else:
                        title = line.move_id.name
                    info['content'].append({
                        'journal_name': line.ref or line.move_id.name,
                        'title': title,
                        'amount': amount_to_show,
                        'currency': currency_id.symbol,
                        'id': line.id,
                        'position': currency_id.position,
                        'digits': [69, self.currency_id.decimal_places],
                    })
                info['title'] = type_payment
                self.outstanding_credits_debits_widget = json.dumps(info)
                self.has_outstanding = True

