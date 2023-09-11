# -*- coding: utf-8 -*-
from .amount_to_text_sv import to_word
from odoo import api, fields, models, _, exceptions

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.multi
    def action_invoice_create(self):
        res=[]
        result = super(SaleOrder, self).action_invoice_create()
        #aqui colocar codigo para poder dividir las facturas
        #print('########################',result)
        i = self.env['account.invoice'].browse(result)
        #Consolidacion de facturas con mismos productos
        #reccorremos las facturas
        borrar=[]
        for inv in i:
          #reccorremos las lineas de cada factura
          for l in inv.invoice_line_ids:
            #selecionamos el producto
            p_id = l.product_id.id
            #print('Producto a Consolidar',p_id)
            #reccorremos nuevamente
            for c in inv.invoice_line_ids:
              #validamos que los productos coinciden pero no son las mismas lineas
              if c.product_id.id == p_id and c.id != l.id and l.id not in borrar:
                #validamos que el precio sea el mismo
                if l.price_unit == c.price_unit:
                  #sumamos las cantidades
                  quantity = l.quantity + c.quantity
                  #print('Cambio de Cantidad',quantity,l.quantity)
                  l.quantity = quantity
                  #borramos la linea que acabamos de sumar
                  borrar.append(c.id)
          
          #print('Listado a borrar',borrar)
          #borramos todas las lineas innecesarias
          ail_borrar = self.env['account.invoice.line'].browse(borrar)
          for l in ail_borrar:
            #print('Borrando Linea',l)
            l.unlink()
          #Division de Facturas por limite de lineas
          lines = len(inv.invoice_line_ids)
          conf = self.env['ir.config_parameter']
          iln = int(conf.get_param('invoice_sv.invoice_line_number'))
          #print('+++++++++',lines,)
          if lines > iln:
            res=result
            #print('Id Factura original',res)
            ti=divmod(lines,iln)
            #print('DIVIDIR',ti)
            if ti[1]!=0:
              ni=ti[0]
            else:
              ni=ti[0]-1
            #print('Cantidad de Facturas a Crear',ni)
            for l in range(ni):
              res.append(inv.copy().id)
            c=0
            
            #print('Listado de Facturas',res)
            for a in res:
              c+=1
              #print('**********',a)
              cl=0
              #calculo de numero inicial y final por factura
              inv_id = self.env['account.invoice'].browse(int(a))
              for ol in inv_id.invoice_line_ids:
                cl+=1
                #print('Calculo de Rango',cl,c,lines)
                if not (cl <= (c*iln) and cl > (c-1)*iln):
                  #print('BORRANDO',ol.product_id.name)
                  ol.unlink()
            
              
          #print('########',res, type(res))
            for so in self:
              for o in so.order_line:
                
                list_l = self.env['account.invoice.line'].search([
                  ('product_id','=',o.product_id.id),
                  ('invoice_id','in',res)])
                for a in list_l:
                  if o.product_id == a.product_id and o.price_unit == a.price_unit:
                    o.write(
                      {
                        'invoice_lines':[(4,a.id)]})
        
          else:
            res=result
          #print('%%%%%%%%%%%%',res)
          for i in self.env['account.invoice'].search([('id','in',res)]):
            i.user_id = inv.user_id.id
        return res

class SaleOrderLine(models.Model):
  _inherit = 'sale.order.line'
  
  @api.depends('invoice_lines.invoice_id.state', 'invoice_lines.quantity')
  def _get_invoice_qty(self):
    super(SaleOrderLine, self)._get_invoice_qty()
    for l in self:
      if l.qty_invoiced > l.product_uom_qty:
        inv_lines = []
        for id_line in l.invoice_lines:
          inv_lines.append(id_line.id)
        #print('##########',list(l.invoice_lines))
        lineas = self.env['sale.order.line'].search([('invoice_lines','in',inv_lines)])
        #print('************',lineas)
        l.qty_invoiced = l.product_uom_qty
        
        