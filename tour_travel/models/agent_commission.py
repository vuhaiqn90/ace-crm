import time
from odoo import fields, models,api
from odoo.tools.translate import _
from odoo.tools import config
from odoo.exceptions import Warning
import string




class agent_commission_invoice(models.Model):
    _name = "agent.commission.invoice"
    _description = "Agent Commision Invoice"
    
    
    @api.model
    def create(self,vals): 
        res = super(agent_commission_invoice, self).create(vals)
        commission = res.create_commission()
        if commission:
            req_no = self.env['ir.sequence'].get('agent.commission.invoice')
            vals['name'] = req_no
            print(res,"res")
            self.write({'name': req_no})
            return res
        else:
            raise Warning("No Commission line for selected data.")
    
#     def create(self, cr, uid, vals, context=None): 
#         res = super(agent_commission_invoice, self).create(cr, uid, vals, context=context)
#         commission = self.create_commission(cr,uid,res)
#         print(commission,"commission")
#         if commission:
#             req_no = self.pool.get('ir.sequence').get(cr,uid,'agent.commission.invoice'),
#             vals['name'] = req_no[0]
#             print(res,"res")
#             self.write(cr, uid, [res], {'name': req_no[0]},context)
#             return res
#         else:
#             raise osv.except_osv(_("Warning"),_("No Commission line for selected data.") )
    
    
    @api.multi
    def unlink(self):
        for obj in self:
            if not obj.state == 'draft':
                raise Warning("Cannot delete other than draft records")
            for line in obj.commission_line:
                line.unlink()
        return super(agent_commission_invoice, self).unlink()
    
    
#     def unlink(self, cr, uid, ids, context):
#         for obj in self.browse(cr, uid, ids):
#             if not obj.state == 'draft':
#                 raise osv.except_osv(_("Warning"),_("Cannot delete other than draft records") )
#             for line in obj.commission_line:
#                 self.pool.get('agent.commission.invoice.line').unlink(cr,uid,line.id)
#         return super(agent_commission_invoice, self).unlink(cr, uid, ids, context = context)
    
    
    @api.multi
    def write(self, vals):
        print(vals,"vals")
        if 'partner_id' in vals and vals['partner_id']:
            raise Warning("Cannot Change Agent at this stage")
        return super(agent_commission_invoice,self).write(vals)
    
#     def write(self, cr, uid, ids,vals,context={}):
#         print(vals,"vals")
#         if vals.__contains__('partner_id') and vals['partner_id']:
#             raise osv.except_osv(_("Warning"),_("Cannot Change Agent at this stage") )
#         obj = self.browse(cr,uid,ids,context)[0]
#         return super(agent_commission_invoice,self).write(cr, uid, ids, vals, context)
    
    
    def create_commission(self):
        result = {}
        obj = self
        tour_obj = self.env['tour.package'].search([('state', 'not in',['draft','done'])])
        if tour_obj:
            commission_list = []
            for tour in tour_obj:
                
                tour_bool = False
                for com_line in obj.partner_id.commission_line_ids:
                    if com_line.tour_id.id == tour.id:
                        commission_list.append(com_line.percentage)
                        tour_bool = True
                if not tour_bool:
                    raise Warning("No Commission Percentage Is Defined for Tour '%s'. Please Configure First !!!"%(tour.name1))
            
            count = 0
            line_data = False
            for tour in tour_obj:
                com_amt = 0.0
                for line in tour.tour_booking_customer_ids:
                    print(line.commission_compute,line.state in ['booked','invoiced','done','draft'],"line.commission_compute:")
                    if not line.commission_compute and line.state in ['booked','invoiced','done']:
                        com_amt = line.tour_cost / commission_list[count]
                        if line.agent_id.id == obj.partner_id.id:
                            exit_data = self.env['agent.commission.invoice.line'].search([('tour_book_id', '=',line.id),('partner_id', '=',line.customer_id.id),
                                                                                                        ('tour_id', '=',tour.id)])
                            if not exit_data:
                                dict = {
                                    'name':line.name,
                                    'tour_book_id':line.id,
                                    'partner_id':line.customer_id.id,
                                    'tour_cost':line.tour_cost,
                                    'commission_amt':com_amt,
                                    'commission_line_id':self.id,
                                    'commission_percentage':commission_list[count],
                                    'tour_id':tour.id,
                                    }
                                print("dict",dict)
                                line_data = True
                                self.env['agent.commission.invoice.line'].create(dict)
                count += 1
            if line_data:
                return True
            else:
                return False
        else:
            return False
    
    
#     def create_commission(self,cr,uid,my_id):
#         result = {}
#         obj = self.browse(cr,uid,my_id)
#         print("obj",obj)
#         tour_search = self.pool.get('tour.package').search(cr, uid, [('state', 'not in',['draft','done'])])
#         if tour_search:
#             commission_list = []
#             tour_obj = self.pool.get('tour.package').browse(cr,uid,tour_search)
#             for tour in tour_obj:
#                 print(tour,"tour")
#                 tour_bool = False
#                 for com_line in obj.partner_id.commission_line_ids:
#                     print(com_line,"com_line")
#                     if com_line.tour_id.id == tour.id: 
#                         commission_list.append(com_line.percentage)
#                         tour_bool = True
#                 if not tour_bool:
#                     raise osv.except_osv(_("Warning"),_("No Commission Percentage Is Defined for Tour '%s'. Please Configure First !!!") %(tour.name1,))
#             count = 0
#             line_data = False
#             for tour in tour_obj:
#                 print("tour==============",tour.tour_booking_customer_ids)
#                 com_amt = 0.0
#                 for line in tour.tour_booking_customer_ids:
#                     print("line",line)
#                     print(line.commission_compute,"line.commission_compute:")
#                     if not line.commission_compute and line.state in ['booked','invoiced','done']:
#                         com_amt = line.tour_cost / commission_list[count]
#                         print("comm_amt",com_amt) 
#                         if line.agent_id.id == obj.partner_id.id:
#                             exit_data = self.pool.get('agent.commission.invoice.line').search(cr, uid, [('tour_book_id', '=',line.id),('partner_id', '=',line.customer_id.id),
#                                                                                                         ('tour_id', '=',tour.id)])
#                             if not exit_data:
#                                 dict = {
#                                     'name':line.name,
#                                     'tour_book_id':line.id,
#                                     'partner_id':line.customer_id.id,
#                                     'tour_cost':line.tour_cost,
#                                     'commission_amt':com_amt,
#                                     'commission_line_id':my_id,
#                                     'commission_percentage':commission_list[count],
#                                     'tour_id':tour.id,
#                                     }
#                                 print("dict",dict)
#                                 line_data = True
#                                 self.pool.get('agent.commission.invoice.line').create(cr,uid,dict)
#                 count += 1
#             if line_data:
#                 return True
#             else:
#                 return False
#         else:
#             return False
    
    
    def _get_total_amt(self):
        res = {}
        total = 0
        for obj in self:
            for i in range (0,len(obj.commission_line)):
                total = total + obj.commission_line[i].commission_amt
            res[obj.id] = total 
        return res
    
#     def _get_total_amt(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         total = 0
#         for obj in self.browse(cr, uid, ids):
#             for i in range (0,len(obj.commission_line)):
#                 total = total + obj.commission_line[i].commission_amt
#             res[obj.id] = total 
#         return res
    
    name = fields.Char("Name",size=50,readonly=True)
    current_date = fields.Date("Date",required=True,readonly=True, states={'draft':[('readonly',False)]},default=lambda *args: time.strftime('%Y-%m-%d'))
#       "tour_id":fields.many2one("tour.package","Tour ID",required=True,readonly=True, states={'draft':[('readonly',False)]}),
    partner_id = fields.Many2one("res.partner","Agent",required=True,readonly=True, states={'draft':[('readonly',False)]})
    commission_line = fields.One2many('agent.commission.invoice.line', 'commission_line_id', 'Invoice Lines',readonly=True, states={'draft':[('readonly',False)]})
    agent_invoice_ids = fields.Many2many('account.invoice','tour_agent_invoice_rel', 'tour_agent_id', 'invoice_id', 'Agent Invoices',readonly=True)
    state = fields.Selection([
                                ('draft', 'Draft'),
                                ('confirm','Confirmed'),
                                ('invoiced', 'Invoiced'),
                                ('done', 'Done'),
                                ('cancel', 'Canceled'),
                                ], 'Status',readonly=True,default=lambda * a: 'draft'
                            )
                
#       "commission_percentage":fields.integer("Commission Percentage",required=True, states={'draft':[('readonly',False)]}),
    total_amt = fields.Float(compute=_get_total_amt, string="Total", store=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist',required=True,readonly=True, states={'draft':[('readonly',False)]})
    
    
#     _defaults = {
#                  'state':lambda * a: 'draft',
#                  'current_date':lambda *args: time.strftime('%Y-%m-%d'),
#                  } 
    
    
    @api.onchange('partner_id')
    def on_change_partner_id(self):
        result = {}
        if self.ids:
            raise Warning("Cannot Change Agent at this stage")
        return {'value': result}
    
#     def on_change_partner_id(self,cr,uid,ids,partner_id):
#         result = {}
#         obj = self.pool.get('res.partner').browse(cr,uid,partner_id)
#         print("obj",obj)
#         print(ids,"ids")
#         if ids:
#             raise osv.except_osv(_("Warning"),_("Cannot Change Agent at this stage") )
#         return {'value': result}
    
    
    
    @api.multi
    def confirm_commission(self):
        for obj in self:
            if not obj.commission_line:
                raise Warning("There is no commission line to process")
            for commission in obj.commission_line:
                if commission.tour_book_id.commission_compute:
                    raise Warning("Commission is already computed or in process for tour booking number '%s'") %(commission.tour_book_id.name)
                else:
                    commission.tour_book_id.write({'commission_compute':True})
            self.write({'state':'confirm'})
        return True
    
#     def confirm_commission(self, cr, uid, ids, *args):
#         for obj in self.browse(cr,uid,ids):
#             if not obj.commission_line:
#                 raise osv.except_osv(_("Warning"),_("There is no commission line to process") )
#             for commission in obj.commission_line:
#                 print("iiiiiiiiiiiiiiiiii    ")
#                 if commission.tour_book_id.commission_compute:
#                     raise osv.except_osv(_("Warning"),_("Commission is already computed or in process for tour booking number '%s'") %(commission.tour_book_id.name) )
#                 else:
#                     self.pool.get('tour.booking').write(cr, uid, commission.tour_book_id.id, {'commission_compute':True})
#             self.write(cr, uid, ids, {'state':'confirm'})
#         return True
    
    @api.multi
    def done(self):
        for obj in self:
            for invoice in obj.agent_invoice_ids:
                if invoice.state != 'paid':
                    raise Warning("Commission is not Paid.")
            self.write({'state':'done'})
        return True
    
#     def done(self, cr, uid, ids, *args):
#         for obj in self.browse(cr,uid,ids):
#             for invoice in obj.agent_invoice_ids:
#                 if invoice.state != 'paid':
#                     raise osv.except_osv(_("Warning"),_("Commission is not Paid.") )
#             self.write(cr, uid, ids, {'state':'done'})
#         return True
    
    @api.multi
    def make_commission_invoice(self):
        for obj in self:
            if not obj.commission_line:
                self.write({'state':'draft'})
                raise Warning("There is no commission line to process")
            acc_id = obj.partner_id.property_account_payable_id.id
            if not acc_id:
                raise Warning("Account is not define for partner")
            
            journal_ids = self.env['account.journal'].search([('type', '=','purchase')], limit=1)
            
            type = 'in_invoice' 
            inv = {
                    'name': obj.name,
                    'origin': obj.name,
                    'type': type,
                    'reference': "Commission Invoice",
                    'account_id': acc_id,
                    'partner_id': obj.partner_id.id,
                    'currency_id': obj.pricelist_id.currency_id.id,
                    'journal_id': len(journal_ids) and journal_ids[0].id or False,
                    'amount_tax':0,
                    'amount_untaxed':obj.total_amt,
                    'amount_total':obj.total_amt,
                }
            
            print("inv",inv)
            inv_id = self.env['account.invoice'].create(inv)
#            print "tax_id",obj.tax_id
            for commission in obj.commission_line:
                line_account_id = commission.tour_id.product_id.product_tmpl_id.property_account_expense_id.id
                if not line_account_id:
                    line_account_id = commission.tour_id.product_id.categ_id.property_account_expense_categ_id.id
                if not line_account_id:
                    raise Warning("Account is not define for  tour '%s'"%(commission.tour_id.product_id.name))
                il = {
                        'name': commission.tour_book_id.name,
                        'account_id': line_account_id,
                        'price_unit':commission.commission_amt, 
                        'quantity': 1.0,
                        'uos_id':  False,
                        'origin':commission.tour_book_id.name,
                        'invoice_id':inv_id.id,
                        'pay_date':obj.current_date,
                        'order_amt':commission.commission_amt,
                        'product_id':commission.tour_id.product_id.id,
                        }
                print("il",il)
                self.env['account.invoice.line'].create(il)
            self._cr.execute('insert into tour_agent_invoice_rel(tour_agent_id,invoice_id) values (%s,%s)', (obj.id, inv_id.id))
        self.write({'state':'invoiced'})
        return True
    
#     def make_commission_invoice(self, cr, uid, ids, *args):
#         for obj in self.browse(cr,uid,ids):
#             if not obj.commission_line:
#                 self.write(cr, uid, ids, {'state':'draft'})
#                 raise osv.except_osv(_("Warning"),_("There is no commission line to process") )
#             acc_id = obj.partner_id.property_account_payable_id.id
#             if not acc_id:
#                 raise osv.except_osv(_("Warning"),_("Account is not define for partner") )
#             
#             journal_obj = self.pool.get('account.journal')
#             journal_ids = journal_obj.search(cr, uid, [('type', '=','purchase')], limit=1)
#             
#             type = 'in_invoice' 
#             inv = {
#                         'name': obj.name,
#                         'origin': obj.name,
#                         'type': type,
#                         'reference': "Commission Invoice",
#                         'account_id': acc_id,
#                         'partner_id': obj.partner_id.id,
# #                        'address_invoice_id': address_invoice_id[0] or False,
#                         'currency_id': obj.pricelist_id.currency_id.id,
#                         'journal_id': len(journal_ids) and journal_ids[0] or False,
#                         'amount_tax':0,
#                         'amount_untaxed':obj.total_amt,
#                         'amount_total':obj.total_amt,
#                         }
#             print("inv",inv)
#             inv_id = self.pool.get('account.invoice').create(cr, uid, inv)
# #            print "tax_id",obj.tax_id
#             for commission in obj.commission_line:
#                 line_account_id = commission.tour_id.product_id.product_tmpl_id.property_account_expense_id.id
#                 if not line_account_id:
#                     line_account_id = commission.tour_id.product_id.categ_id.property_account_expense_categ_id.id
#                 if not line_account_id:
#                     raise osv.except_osv(_("Warning"),_("Account is not define for  tour '%s'") %(commission.tour_id.product_id.name) )
#                 il = {
#                         'name': commission.tour_book_id.name,
#                         'account_id': line_account_id,
#                         'price_unit':commission.commission_amt, 
#                         'quantity': 1.0,
#                         'uos_id':  False,
#                         'origin':commission.tour_book_id.name,
#                         'invoice_id':inv_id,
#                         'pay_date':obj.current_date,
#                         'order_amt':commission.commission_amt,
#                         'product_id':commission.tour_id.product_id.id,
#                         }
#                 print("il",il)
#                 self.pool.get('account.invoice.line').create(cr, uid, il,)
#             cr.execute('insert into tour_agent_invoice_rel(tour_agent_id,invoice_id) values (%s,%s)', (obj.id, inv_id))
#         self.write(cr, uid, ids, {'state':'invoiced'})
#         return True
    



class agent_commission_invoice_line(models.Model):
    _name = "agent.commission.invoice.line"
    _description = " Commision Invoice Line"
    
    name = fields.Char("Name",size=50,required=True,readonly=True)
    tour_id = fields.Many2one("tour.package","Tour ID",required=True,readonly=True)
    tour_book_id = fields.Many2one("tour.booking","Tour Booking ID",required=True,readonly=True)
    commission_percentage = fields.Float("Commission Percentage",required=True,readonly=True)
    partner_id = fields.Many2one("res.partner","Customer Name",required=True,readonly=True)
    tour_cost = fields.Float('Total Cost', required=True,readonly=True)
    commission_amt = fields.Float("Commission Amount",required=True,readonly=True)
    commission_line_id = fields.Many2one("agent.commission.invoice","Commission ID",readonly=True)
    
    
    @api.onchange('tour_book_id')
    def on_change_tour_book_id(self):
        result = {}
        result['name'] = self.tour_book_id.name
        print()
        return {'value': result}
    
#     def on_change_tour_book_id(self,cr,uid,ids,tour_book_id):
#         result = {}
#         obj = self.pool.get('tour.booking').browse(cr,uid,tour_book_id)
#         result['name'] = obj.name
#         return {'value': result}
    
