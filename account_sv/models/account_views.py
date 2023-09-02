# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.osv import expression

class AccountViews(models.Model):
  _name = 'account.views'
  _description = 'Cuentas de Vistas'
  _parent_name = "parent_id"
  _parent_store = True
  _parent_order = 'code'
  _order = 'code'
  _inherit = [
        'mail.thread',
        'mail.activity.mixin',
        'portal.mixin'
      ]
  
  name = fields.Char('Nombre', index=True)
  code = fields.Char('Codigo', index=True)
  company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get('account.views'))
  level = fields.Integer('Nivel')
  sequence = fields.Integer('Secuencia')
  active = fields.Boolean('Activo', default=True)
  parent_id = fields.Many2one('account.views','Cuenta Padre', ondelete='cascade')
  parent_left = fields.Integer('Left Parent', index=True)
  parent_right = fields.Integer('Right Parent', index=True)
  child_ids = fields.One2many('account.views', 'parent_id', 'Cuentas Hijas')
  mayor = fields.Boolean('Es Mayor', default=True)
  diario_mayor = fields.Boolean('Mostrar En Diario Mayor',
                                index=True,
                                store=True,
                                compute='_diario_mayor')
  cuenta_mayor = fields.Many2one('account.views',
                                 string='Cuenta de Mayor',
                                 compute='_acc_mayor',
                                 store=True,
                                 index=True,
                                 readonly=False
                                 )
  account_ids = fields.One2many('account.account',
                                'account_view_id',
                                 string='Cuentas de Apuntes',
                                 )
  
  primary = fields.Boolean('color', compute='_primary')
  success = fields.Boolean('color', compute='_success')
  warning = fields.Boolean('color', compute='_warning')
  _sql_constraints = [
        ('code_company_uniq', 'unique (code,company_id)', 'The code of the account must be unique per company !')
    ]
  
  def len_account_mayor(self, code):
    i=0
    for l in code:
      if l in ['1','2','3','4','5','6','7','8','9','0']:
        i+=1
      else:
        return i
      

  @api.depends('code')
  def _acc_mayor(self):
    for l in self:
      len_code = self.len_account_mayor(l.code)
      if len_code:
        if len(l.code)> len_code:
          ids=self.search([('code','=',l.code[:len_code])])
          l.cuenta_mayor = ids

  @api.depends('code')
  def _diario_mayor(self):
    for l in self:
      len_code = self.len_account_mayor(l.code)
      if len(l.code)==len_code:
        l.diario_mayor = True
      else:
        l.diario_mayor = False
      
  
  @api.depends('code')
  def _primary(self):
    for l in self:
      if len(l.code)==1:
        l.primary = True
  @api.depends('code')
  def _success(self):
    for l in self:
      if len(l.code)==2:
        l.success = True
  @api.depends('code')
  def _warning(self):
    for l in self:
      if len(l.code)>3 and l.account_ids:
        l.warning = True
  #funcion para limpiar todas las cuentas sin agregadas automaticamente
  @api.multi
  def clean_accounts(self):
    self.account_ids = False
    
  def tmp_code(self,code):
      tmp_code = code
      for l in code:
        if l not in ['1','2','3','4','5','6','7','8','9','0']:
          tmp_code=code.replace(l,'')
      return tmp_code
  
  @api.onchange('code')
  def _onchange_code(self):
    if self.code:
      len_code = self.len_account_mayor(self.code)
      tmp_code = self.tmp_code(self.code)
      self.sequence = tmp_code
      self.level = len(tmp_code)
      if len(tmp_code) > len_code:
        self.mayor = False
        self.account_ids = self.env['account.account'].search([
          ('code','ilike',self.code+'%')])
      else:
        self.mayor = True
        self.clean_accounts()
        
  @api.model
  def create(self, vals):
    if vals.get('code'):
      vals['level'] = len(self.tmp_code(vals.get('code')))
    return super(AccountViews, self).create(vals)

  @api.multi
  def write(self, vals):
    if vals.get('code'):
      tmp_code = self.tmp_code(vals.get('code'))
      if len(tmp_code) > 5:
        vals['mayor']=False
      if 'account_ids' in vals:
        if not vals.get('account_ids')[0][1]:
          vals['mayor']=True
          vals['account_ids']=False
    return super(AccountViews, self).write(vals)

  @api.model
  def name_search(self, name, args=None, operator='ilike', limit=100):
    args = args or []
    domain = []
    if name:
      domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
      if operator in expression.NEGATIVE_TERM_OPERATORS:
        domain = ['&', '!'] + domain[1:]
    accounts = self.search(domain + args, limit=limit)
    return accounts.name_get()

  @api.multi
  @api.depends('name', 'code')
  def name_get(self):
    result = []
    for account in self:
      name = account.code + ' ' + account.name
      result.append((account.id, name))
    return result
    
  @api.one
  @api.returns('self', lambda value: value.id)
  def copy(self, default=None):
    default = dict(default or {})
    default.setdefault('code', _("%s (copy)") % (self.code or ''))
    return super(AccountViews, self).copy(default)
  
class AccountAccount(models.Model):
  _inherit = 'account.account'
  
  account_view_id = fields.Many2one('account.views',string="Cuenta de Mayor")

  def len_account_mayor(self, code):
    i=0
    for l in code:
      if l in ['1','2','3','4','5','6','7','8','9','0']:
        i+=1
      else:
        return i


  @api.onchange('code')
  def _onchange_code(self):
    len_code = self.len_account_mayor(self.code)
    code_mayor = self.code[:len_code]
    id_mayor = self.env['account.views'].search([('code','=', code_mayor)]).ids
    self.account_view_id = id_mayor
  
