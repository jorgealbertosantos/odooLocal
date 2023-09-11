# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountChart(models.TransientModel):
  _name = 'account.chart.wizard'
  
  @api.model
  def _search_accounts(self):
    self.env.cr.execute("select id,code from account_views where code like '1%' OR code like '2%' OR code like '3%';")
    data = self.env.cr.dictfetchall()
    ids = []
    for a in data:
      if a.get('code')[0] in ['1','2','3']:
        ids.append(a.get('id'))
    return self.env['account.views'].search([('id','in',ids)]) or False
    #return self.env['account.views'].search([]) or False
  
  @api.model
  def _get_date_start(self):
    year = fields.Date.today()
    date = str(year[:4])+'-01-01'
    return date
    
  account_views_ids = fields.Many2many('account.views',
                                       string='Cuentas',
                                       default=lambda self: self._search_accounts())
  debit_credit = fields.Boolean('Mostrar Columnas Cargos y Abonos')
  
  company_id = fields.Many2one('res.company',
              string='Compañia',
              change_default=True,
              default=lambda self: self.env.user.company_id.id)

  display_account = fields.Selection([
      ('all','Todas'),
      ('not_zero','Saldo Distinto De Cero'),
      ('movement','Con Movimiento')
    ],
    'Mostras Cuentas',
    default='all',
    required=True)
  
  display_report = fields.Selection([
      ('bg','Cuentas de Balance'),
      ('er','Cuentas de Resultado'),
      ('liq','Cuentas de Liquidacion')
      ],
    'Tipos de Cuentas ha Mostrar',
    default='bg',
    required=True)
  
  move_draft = fields.Boolean('Incluir asientos no validados')
  
  date_start = fields.Date('Fecha Inicial',
                           default=lambda self: self._get_date_start())
  date_stop = fields.Date('Fecha Final',
                          default= fields.Date.today())

  @api.onchange('display_report')
  def _onchange_display_report(self):

    if self.display_report == 'bg':
      self.env.cr.execute("select id,code from account_views where code like '1%' OR code like '2%' OR code like '3%';")
      data = self.env.cr.dictfetchall()
      ids = []
      for a in data:
        if a.get('code')[0] in ['1','2','3']:
          ids.append(a.get('id'))
      self.account_views_ids = ids

    if self.display_report == 'er':
      self.env.cr.execute("select id,code from account_views where code like '4%' OR code like '5%' OR code like '6%';")
      data = self.env.cr.dictfetchall()
      ids = []
      for a in data:
        if a.get('code')[0] in ['4','5','6']:
          ids.append(a.get('id'))
      self.account_views_ids = ids

    if self.display_report == 'liq':
      self.env.cr.execute("select id,code from account_views where code like '7%' OR code like '8%' OR code like '9%';")
      data = self.env.cr.dictfetchall()
      ids = []
      for a in data:
        if a.get('code')[0] in ['7','8','9']:
          ids.append(a.get('id'))
      self.account_views_ids = ids
      
  @api.multi
  def clean_accounts(self):
    self.account_views_ids = False
    return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.chart.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
             }  
  @api.multi
  def _get_printed_report_name(self):
    self.ensure_one()
    name = 'Plan Contable ' + fields.Date.today()
    return name

  @api.multi
  def acc_data(self,i,pi,level,code,name,debit,credit,balance):
      acc={}
      acc['id']=i
      acc['parent_id']=pi
      acc['level']=level
      acc['code']=code
      acc['name']=name
      acc['debit']=debit
      acc['credit']=credit
      acc['balance']=balance
      return acc
  @api.multi
  def get_move(self):
    if self.move_draft:
      state = 'draft'
      state2= 'posted'
    else:
      state = 'posted'
      state2= 'posted'
    
    params = (state,state2)
    request = "SELECT id FROM account_move as am WHERE am.state = %s OR am.state = %s"
    self.env.cr.execute(request, params)
    moves = self.env.cr.dictfetchall()
    m_ids = []
    for m in moves:
      m_ids.append(m.get('id'))
    return m_ids
  
  @api.multi
  def get_accounts(self):
      """Funcion que calcula el saldo de todas las cuentas
      en el campo account_views_ids y sus hijas consecutivamente
      devuelve un dicionario con
      * codigo
      * nombre
      * cargos
      * abonos
      * saldos
      * padre
      """
      res=[]
      ids_acc=self.account_views_ids.ids
      move_ids = self.get_move()
      # primero buscamos todas la cuentas que poseen
      # cuentas de apuntes para calcular el saldo inicial
      cuentas_mayor = self.env['account.views'].search([
        ('account_ids','=',False),
        ('id','in', ids_acc)])
      
      for a in cuentas_mayor:
        res.append(self.acc_data(a.id,
                                 a.parent_id.id or False,
                                 a.level,
                                 a.code,
                                 a.name,
                                 0,
                                 0,
                                 0))
      
      cuentas_menor = self.env['account.views'].search([
        ('account_ids','!=',False),
        ('id','in', ids_acc)])
      #diccionario con datos de todas las cuentas
      data = self.get_data(move_ids)
      
      for a in cuentas_menor:
        #obtenemos datos de cada cuenta
        if data:
          for l in data:
            if l in a.account_ids.ids:
              debit = data[l].get('debit')
              credit = data[l].get('credit')
              balance = data[l].get('balance')
              name = data[l].get('name')
              code = data[l].get('code')
              #agregamos los valores al resultado
              res.append(self.acc_data('menor',
                                       a.id,
                                       a.level,
                                       code,
                                       name,
                                       debit,
                                       credit,
                                       balance))
        #se agrega la cuenta que agrupa el saldo
        res.append(self.acc_data(a.id,
                                 a.parent_id.id or False,
                                 a.level,
                                 a.code,
                                 a.name,
                                 0,
                                 0,
                                 0))
        
      # obtenemos el nivel maximo
      self.env.cr.execute("select MAX(level) from account_views;")
      max_l = self.env.cr.dictfetchall()[0].get('max')
      # hacemos recorridos de las cuentas por nivel para actualizar todos los saldos
      for m in range(max_l):
        #actualizamos saldo de cuentas mayor
        for l in res:
          if l.get('level') == (max_l - m):
            res = self.update_data(res,l,max_l)
            
      # Revisamos tipo de visualizacion para adaptar los datos
      if self.display_account != 'all':
        for m in range(max_l):
          for z in res:
            if self.display_account == 'not_zero':
              if z.get('balance') == 0:
                index = res.index(z)
                res.pop(index)
              
            if self.display_account == 'movement':
              if z.get('credit') == 0  and z.get('debit') == 0 and z.get('balance') == 0:
                index = res.index(z)
                res.pop(index)
        
      res.sort(key=lambda c: c.get('code'))
      return res
  
  @api.multi
  def update_data(self,res,l,max_l):
    for a in res:
      if a.get('id') == l.get('parent_id'):
        if a.get('id') != 'menor':
          debit = a.get('debit') + l.get('debit')
          credit = a.get('credit') + l.get('credit')
          balance = a.get('balance') + l.get('balance')
          a['debit']= debit
          a['credit']= credit
          a['balance']= balance
    return res
    
  @api.multi
  def get_data(self,m_ids):
      res = {}
      if self.display_report == 'bg':
        params = (self.date_stop,tuple(m_ids))
        request = "SELECT account_id AS id, aa.name, aa.code, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance FROM account_move_line as aml, account_account as aa WHERE aml.account_id = aa.id AND aml.date <= %s AND aml.move_id IN %s GROUP BY account_id,aa.name,aa.code"
      else:
        params = (self.date_stop,self.date_start,tuple(m_ids))
        request = "SELECT account_id AS id, aa.name, aa.code, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance FROM account_move_line as aml, account_account as aa WHERE aml.account_id = aa.id AND aml.date <= %s AND aml.date >= %s AND aml.move_id IN %s GROUP BY account_id,aa.name,aa.code"

      self.env.cr.execute(request, params)
      for row in self.env.cr.dictfetchall():
        res[row['id']] = row      
      return res
  
  @api.multi
  def print_report(self):
      return self.env.ref('contabilidad.account_chart_report').report_action(self)
