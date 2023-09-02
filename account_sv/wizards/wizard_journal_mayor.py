# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, exceptions
from datetime import datetime,timedelta
from calendar import monthrange


class JournalMayor(models.TransientModel):
  _name = 'journal.mayor.wizard'
  
  @api.multi
  def create_view(self,type_view,acc,date_start,date_stop):
    if type_view == 'bg':
      tools.drop_view_if_exists(self.env.cr, 'account_mayor_data_bg')
      request="""
        CREATE OR REPLACE VIEW account_mayor_data_bg AS (
          SELECT
            avm.id AS id,
            avm.code AS code,
            avm.name AS name,
            av.date AS date,
            SUM(av.debit) AS debit,
            SUM(av.credit) AS credit
          FROM
            account_views AS avm
            RIGHT JOIN 
              (SELECT
                av.id AS id,
                av.cuenta_mayor AS cuenta_mayor,
                aml.date AS date,
                SUM(debit) AS debit,
                SUM(credit) AS credit
              FROM
                account_views AS av
                FULL JOIN account_account AS aa
                ON aa.account_view_id = av.id
                FULL JOIN account_move_line AS aml
                ON aml.account_id = aa.id
                FULL JOIN account_move AS am
                ON aml.move_id = am.id
              WHERE
                av.id in %s AND
                aml.date <= %s
              GROUP BY
                av.id,
                av.cuenta_mayor,
                aml.date,
                av.level
                ) AS av
            ON av.cuenta_mayor = avm.id
          GROUP BY
            avm.id,
            avm.code,
            avm.name,
            av.date
            )
        """
      params=(tuple(acc),date_stop)
      
    
    if type_view == 'er':
      tools.drop_view_if_exists(self.env.cr, 'account_mayor_data_er')
      request="""
        CREATE OR REPLACE VIEW account_mayor_data_er AS (
          SELECT
            avm.id AS id,
            avm.code AS code,
            avm.name AS name,
            av.date AS date,
            SUM(av.debit) AS debit,
            SUM(av.credit) AS credit
          FROM
            account_views AS avm
            RIGHT JOIN 
              (SELECT
                av.id AS id,
                av.cuenta_mayor AS cuenta_mayor,
                aml.date AS date,
                SUM(debit) AS debit,
                SUM(credit) AS credit
              FROM
                account_views AS av
                FULL JOIN account_account AS aa
                ON aa.account_view_id = av.id
                FULL JOIN account_move_line AS aml
                ON aml.account_id = aa.id
                FULL JOIN account_move AS am
                ON aml.move_id = am.id
              WHERE
                av.id in %s AND
                aml.date >= %s AND
                aml.date <= %s
              GROUP BY
                av.id,
                av.cuenta_mayor,
                aml.date,
                av.level
                ) AS av
            ON av.cuenta_mayor = avm.id
          GROUP BY
            avm.id,
            avm.code,
            avm.name,
            av.date
            )
        """
      params=(tuple(acc),date_start,date_stop)
      
    self.env.cr.execute(request,params)
    return True
    
  company_id = fields.Many2one('res.company',
            string='Compañia',
            change_default=True,
            default=lambda self: self.env.user.company_id.id)

  date_stop = fields.Date('Fecha Final',
                        default= fields.Date.today())
  
  mes = fields.Selection(
    [
      ('01','Enero'),
      ('02','Febrero'),
      ('03','Marzo'),
      ('04','Abril'),
      ('05','Mayo'),
      ('06','Junio'),
      ('07','Julio'),
      ('08','Agosto'),
      ('09','Septiembre'),
      ('10','Octubre'),
      ('11','Noviembre'),
      ('12','Diciembre'),
      ],
    'Mes',
    default=fields.Datetime.now()[5:7],
    required=True,
    )
  
  @api.onchange('date_stop')
  def _onchange_date_stop(self):
    if self.mes != self.date_stop[5:7]:
      self.mes = self.date_stop[5:7]
    
  @api.onchange('mes')
  def _onchange_mes(self):
    if self.mes:
      mes = self.mes
      date = self.date_stop
      if mes != date[5:7]:
        year = fields.Datetime.from_string(date).year
        days = monthrange(year,int(mes))
        self.date_stop= str(year) + '-' + str(mes) + '-' + str(days[1])
    
  @api.multi
  def _get_printed_report_name(self):
    self.ensure_one()
    name = 'Diario Mayor ' + fields.Date.today()
    return name
  
  @api.multi
  def convert_balance(self, code, balance):
    #print(code, balance)
    if code[0] not in ['1','4']:
      balance = balance * -1
    else:
      balance = balance
    return float(balance)
  #@api.multi
  def get_day(self):
    days = []
    #Calculamos las Fechas
    date_stop = fields.Datetime.from_string(self.date_stop)
    date_start = datetime(date_stop.year,int(self.mes),1)
    #validamos que no sean iguales
    if date_start == date_stop:
      f={}
      f['date_start']=date_start
      f['date']=date_stop
      f['dia']=date_stop.strftime('%d')
      days.append(f)
    else:
      #determinamos cuantos dias son la diferencia
      #sumamos uno por el ultimo dia no tomado en cuenta
      n_day = ((date_stop - date_start).days) + 1
      for n in range(n_day):
        f={}
        d = date_start + timedelta(days=n)
        f['date_start']=date_start
        f['date']=d.strftime("%Y-%m-%d")
        f['dia']=d.strftime('%d')
        days.append(f)
      days.sort(key=lambda c: c.get('dia'))
    return days

  @api.multi
  def get_move(self):
    result = self.env['account.move'].search(
      [
        ('date','<=',self.date_stop),
        ('state','=', 'draft')
        ]
      )
    if result:
      raise exceptions.UserError('Es Necesario Validar asientos en estado Borrador para poder imprimir este reporte')
    else:
      return True
  
  @api.multi
  def get_accounts(self):
    accounts={}
    acc_b=[]
    acc_e=[]
    self.env.cr.execute("select id,code from account_views;")
    table_acc = self.env.cr.dictfetchall()
    for l in table_acc:
      if l.get('code'):
        if l.get('code')[0] in ['1','2','3']:
          acc_b.append(l.get('id'))
        if l.get('code')[0] not in ['1','2','3']:
          acc_e.append(l.get('id'))
    accounts['balance']=acc_b
    accounts['resultado']=acc_e
    return accounts
  
  @api.multi
  def get_data_accounts(self):
    res=[]
    
    request = """
            SELECT
              *
            FROM
              account_mayor_data_bg
            """
    self.env.cr.execute(request)
    table = self.env.cr.dictfetchall()
    for l in table:
      res.append(l)
    
    request = """
            SELECT
              *
            FROM
              account_mayor_data_er
            """
    self.env.cr.execute(request)
    table = self.env.cr.dictfetchall()
    for l in table:
      res.append(l)
    return res
  
  @api.multi
  def get_init(self):
    #creamos la vista con los datos
    date_stop = fields.Datetime.from_string(self.date_stop)
    date_start=datetime(date_stop.year,int(self.mes),1)
    accounts = self.get_accounts()
    self.create_view('bg',accounts.get('balance'),date_start,date_stop)
    self.create_view('er',accounts.get('resultado'),date_start,date_stop)
    return True

  @api.multi
  def get_balance_old(self, code, date):
    date_stop = fields.Datetime.from_string(self.date_stop)
    date_start = datetime(date_stop.year,1,1)
    balance = 0.0
    if code[:1] in ['1','2','3']:
      request="""
          SELECT
            (sum(debit) - sum(credit)) AS balance
          FROM
            account_mayor_data_bg
          WHERE
            code = %s
            AND
            date < %s
          GROUP BY
            code
        """
      params=(code,date)
    else:
      request="""
          SELECT
            (sum(debit) - sum(credit)) AS balance
          FROM
            account_mayor_data_er
          WHERE
            code = %s
            AND
            date >= %s
            AND
            date < %s
          GROUP BY
            code
        """
      params=(code,date_start,date)  
    self.env.cr.execute(request,params)
    for b in self.env.cr.dictfetchall():
      #print(b)
      balance = b.get('balance')
    return balance

  @api.multi
  def get_data_line(self, date):
    date = fields.Datetime.from_string(date)
    date_stop = datetime(date.year,date.month,date.day)
    date_start = datetime(date.year,1,1)
    res=[]
    #consulta de cuentas de balance
    request = """
            SELECT
             amdb.id,
             amdb.code,
             amdb.name,
             SUM(amd.balance_old) AS balance_old,
             SUM(amdb.debit) AS debit,
             SUM(amdb.credit) AS credit,
             SUM(amd.balance_old) + (SUM(amdb.debit) - SUM(amdb.credit)) AS balance
            FROM
              account_mayor_data_bg AS amdb
              FULL JOIN 
              (SELECT
                  id,
                  code,
                  (sum(debit) - sum(credit)) AS balance_old
                FROM
                  account_mayor_data_bg
                WHERE
                  date < %s
                GROUP BY
                  id,
                  code
              ) AS amd
            ON
              amd.id = amdb.id
            WHERE
              date = %s
            GROUP BY
              amdb.id,
              amdb.code,
              amdb.name
            """
    params=[fields.Date.to_string(date_stop),fields.Date.to_string(date_stop)]
    self.env.cr.execute(request,params)
    table = self.env.cr.dictfetchall()
    for l in table:
      res.append(l)
    #cuentas de resultado
    request = """
            SELECT
             amdb.id,
             amdb.code,
             amdb.name,
             SUM(amd.balance_old) AS balance_old,
             SUM(amdb.debit) AS debit,
             SUM(amdb.credit) AS credit,
             SUM(amd.balance_old) + (SUM(amdb.debit) - SUM(amdb.credit)) AS balance
            FROM
              account_mayor_data_er AS amdb
              FULL JOIN 
              (SELECT
                  code,
                  (sum(debit) - sum(credit)) AS balance_old
                FROM
                  account_mayor_data_er
                WHERE
                  date < %s
                  AND
                  date >= %s
                GROUP BY
                  code
              ) AS amd
            ON
              amd.code = amdb.code
            WHERE
              date = %s
            GROUP BY
              amdb.id,
              amdb.code,
              amdb.name
              """
    params=(fields.Date.to_string(date_stop), fields.Date.to_string(date_start), fields.Date.to_string(date_stop))
    self.env.cr.execute(request,params)
    table = self.env.cr.dictfetchall()
    for l in table:
      res.append(l)

    return res

  #@api.multi
  def get_data(self):
    self.get_init()
    res=[]
    tmp2=[]
    #tmpini = []
    days = self.get_day()
    #obtenemos los datos correspondientes a las cuentas de balance
    #data = self.get_data_accounts()
    #print(data)
    for d in days:
      res2={}
      tmp=[]
      tmp3=[]
      for l in self.get_data_line(d.get('date')):
        #print(l)
        if not l.get('balance_old'):
          l['balance_old']=0
        if not l.get('balance'):
          if l.get('credit')==0 and l.get('debit')==0:
            l['balance']=0
          else:
            l['balance']=l.get('debit') - l.get('credit')
        tmp.append(l)
      
      '''
      if d.get('dia')=='01':
        
        for l in self.get_data_init():
          tmp.append(l)
        tmpini=tmp
      else:
        print(tmpini,'DIA 1')
        for l in data:
          
          #print(l.get('date'),d.get('date'))
          #l es linea dentro de data con la estructura "id,code,name,date,debit,credit"
          if l.get('code')[0] in ['1','2','3']:
            if l.get('date')== d.get('date'):
              l2=l
              #if d.get('dia')==1:
              #balance_old = self.get_balance_old(l.get('code'),l.get('date'))
              balance_old = tmpini.index()
              l2['balance_old']= balance_old
              l2['balance']=(balance_old + l.get('debit')) - l.get('credit') 
              tmp.append(l2)
        tmp2=tmp
        #print(tmp,'----------------------------')
      '''
      if not d.get('dia')=='01':
        #print('Datos del Dia',tmp,'++++++++++++++++++++')
        #print('Datos del Dia Anterior',tmp2,'----++++++++++++++++++++')
        
        for l in tmp:
          for a in tmp2:
            if a.get('code') == l.get('code'):
              tmp2.pop(tmp2.index(a))
        #print('Datos del Dia Anterior Actualizados',tmp2,'*******----++++++++++++++++++++')
        if tmp2:
          #print(tmp2)
          for l in tmp2:
            #print(l.get('balance'))
            if l.get('balance') != 0.0:
              a={}
              a['balance_old']=l.get('balance')
              a['debit']=0
              a['credit']=0
              a['balance']=l.get('balance')
              a['id']=l.get('id')
              a['code']=l.get('code')
              a['name']=l.get('name')
              #print(a)
              tmp3.append(a)
          #print('Datos a Insertar', tmp3,'***************')
          #print('Dias',d,'====================')
          #print('Datos antes de insertar',tmp,'====================')
          if tmp3:
            for l in tmp3:
              tmp.append(l)
          #print('////////////////////====================')    
          #print('Datos Actualizados',tmp,'====================')
      
      
      #print(tmp,'============================')
          
      tmp.sort(key=lambda c: c.get('code'))
      #print('DATOS ORDENADOS',tmp,'============================')
      res2[d.get('dia')]=tmp
      #print('DATOS ESTRUCTURADOS',res2,'/////////////////')
      res.append(res2)
      tmp2=[]
      tmp2.extend(tmp)
    #print('DATOS FINALES',res,'************')
    '''
    Buscar todas la cuentas con saldos distintos de cero anteriores al primer dia de cada mes.
    Sumar cargos y abonos deben ser iguales en teoria.
    '''
    #print(res)
    #ordenamos por codigo las cuentas
    #res.sort(key=lambda c: c.[1].get('code'))
    #devolver un diccionario con datos por dia
    #devolver un diccionario con datos de cuentas por dia.
    return res
  
  @api.multi
  def print_report(self):
    self.get_move()
    return self.env.ref('contabilidad.journal_mayor_report').report_action(self)