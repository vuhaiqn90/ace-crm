from odoo import fields, models, api
from odoo.tools.translate import _


class tour_information(models.TransientModel):
    _name='tour.information'
    _description = 'Tour Information'
    
    
    @api.onchange('category_type')
    def onchange_category(self):
        val={}
        val['flag']=self.category_type
        return {'value':val}
    
#     def onchange_category(self,cr,uid,ids,vals,context=None):
#         print(vals)
#         val={}
#         val['flag']=vals
#         return {'value':val}
    
    
    def send_info(self):
        obj = self
        record_id = self._context and self._context.get('active_id', False)
        email_to = ''
        if obj[0].crm_records:
            for rec in obj[0].crm_records:
                email_to = email_to + rec.email_from+','
        if obj[0].partner:
            for rec in obj[0].partner:
                email_to = email_to + rec.email +','
        
        email_template_obj = self.env['mail.template']
        if email_to:
            template = self.env['ir.model.data'].get_object('tour_travel', 'email_template_package_information')
            template.write({
                           'email_from':'admin@gmail.com',
                           'email_to':email_to,
                        })  
            template.send_mail(record_id , force_send=True)
    
#     def send_info(self,cr,uid,ids,context=None):
#         obj = self.browse(cr,uid,ids,context=None)
#         record_id = context and context.get('active_id', False)
#         email_to = ''
#         if obj[0].crm_records:
#             for rec in obj[0].crm_records:
#                 email_to = email_to + rec.email_from+','
#         if obj[0].partner:
#             for rec in obj[0].partner:
#                 email_to = email_to + rec.email +','
#         
#         email_template_obj = self.pool.get('mail.template')
#         if email_to:
#             template = self.pool.get('ir.model.data').get_object(cr, uid, 'tour_travel', 'email_template_package_information')
#             email_template_obj.write(cr,uid,[template.id],{
#                                                        'email_from':'admin@gmail.com',
#                                                        'email_to':email_to,
#                                                        })  
#             email_template_obj.send_mail(cr, uid, template.id, record_id , True, context=context)

    
    
    category_type = fields.Selection([('lead','Leads'),('opportunity','Opportunity'),('customer','Customer')],'Category')
    email_list = fields.Text("Email list")
    crm_records = fields.Many2many('crm.lead','crm_tour_rel','tour_id','crm_id','Leads / Opportunity')
    partner = fields.Many2many('res.partner','partner_tour_rel','tour_id','partner_id' ,'Partner / Customer')
    flag = fields.Char('Flag',size=16)



class tour_partner_invoices(models.TransientModel):
    _name='tour.partner.invoices'
    _description = 'Tour Partner Invoices'
    
    partner = fields.Many2many('res.partner','tour_partner_invoice_rel','tour_id','partner_id' ,'Partner / Customer')
    
    
    def send_info(self):
        
        if 'active_ids' in self._context and self._context['active_ids']:
            if len(self._context['active_ids']) > 1 :
                raise ("Please select one tour at a time.")
        
        rec = self
        invoice_obj = self.env['account.invoice']
        invoice_line_obj = self.env['account.invoice.line']
        
        tour_package = self.env['tour.package'].browse(self._context['active_id'])
        subtotal = tour_package.subtotal
        tax_amt = tour_package.tax_amt
        tot = tour_package.total_amt
        
        
        for i in rec:
            for partner in i.partner:
                cust_id = partner.id
                currency = partner.property_product_pricelist.currency_id.id
                cust_acc_id = partner.property_account_receivable.id
        
                jour_id = invoice_obj._get_journal()
                invoice_id = invoice_obj.create({
                                                 'partner_id' : cust_id,
                                                 'journal_id' : jour_id.id,
                                                 'account_id' : cust_acc_id,
                                                 'currency_id' : currency,
                                                 'amount_untaxed' : subtotal,
                                                 'amount_tax' : tax_amt,
                                                 'amount_total' : tot,
                                                 'product_id' :tour_package.product_id.id,
                                                 })
                
                
               
        #*****************valuse for Invoice line creation account.invoice.line
                for line in tour_package.product_line_id:
                    tax = []
                    product_id = line.product_id.id
                    desc = line.name
                    if line.product_id.property_account_income:
                        line_account_id = line.product_id.property_account_income.id
                    else:
                        line_account_id = line.product_id.categ_id.property_account_income_categ.id
                    pro_qty = line.qty
                    unit_price = line.price_unit
                    for v in line.tax_id:
                        tax.append(v.id)
                    
                    invoice_line_obj.create({
                                             'invoice_id' : invoice_id,
                                             'product_id' : product_id,
                                             'price_unit' : unit_price,
                                             'quantity' : pro_qty,
                                             'invoice_line_tax_id' : [(6, 0, tax)],
                                             'account_id' : line_account_id,
                                             'name' : desc,
                                        })
                invoice_id.button_reset_taxes()
        return True
    
#     def send_info(self,cr,uid,ids,context=None):
#         print("-------------------------------Into invoice create----------------------")
#         print("\n\nidssss-----------------",ids)
#         print("context---------------------",context)
#         
#         if 'active_ids' in context and context['active_ids']:
#             if len(context['active_ids']) > 1 :
#                 raise osv.except_osv(_('Error'),_("Please select one tour at a time."))
#         
#         rec = self.browse(cr, uid, ids)
#         print("partner Idsssss------",rec)
#         invoice_obj = self.pool.get('account.invoice')
#         invoice_line_obj = self.pool.get('account.invoice.line')
#         
#         cust_id = []
#         currency = []
#         cust_acc_id = []
#         subtotal = []
#         tax_amt = []
#         tot = []
#         product_id = []
#         pro_qty = []
#         unit_price = []
#         total = []
#         sub_total = []
#         line_account_id = []
#         desc = "" 
#         tax = []   
#         tour_package = self.pool.get('tour.package').browse(cr, uid, context['active_id'])
#         subtotal = tour_package.subtotal
#         tax_amt = tour_package.tax_amt
#         tot = tour_package.total_amt
#         
#         
#         for i in rec:
#             for partner in i.partner:
# 
#                 cust_id = partner.id
#                 currency = partner.property_product_pricelist.currency_id.id
#                 cust_acc_id = partner.property_account_receivable.id
#         
#                 jour_id = invoice_obj._get_journal(cr, uid, context)
#                 invoice_id = invoice_obj.create(cr, uid, 
#                                                 {
#                                                  'partner_id' : cust_id,
#                                                  'journal_id' : jour_id,
#                                                  'account_id' : cust_acc_id,
#                                                  'currency_id' : currency,
#                                                  'amount_untaxed' : subtotal,
#                                                  'amount_tax' : tax_amt,
#                                                  'amount_total' : tot,
#                                                  'product_id' :tour_package.product_id.id,
#                                                  })
#                 
#                 
#                
#         #*****************valuse for Invoice line creation account.invoice.line
#                 for line in tour_package.product_line_id:
#                     product_id = []
#                     pro_qty = []
#                     unit_price = []
#                     line_account_id = []
#                     desc = "" 
#                     tax = []
#                     product_id = line.product_id.id
#                     desc = line.name
#                     if line.product_id.property_account_income:
#                         line_account_id = line.product_id.property_account_income.id
#                     else:
#                         line_account_id = line.product_id.categ_id.property_account_income_categ.id
#                     pro_qty = line.qty
#                     unit_price = line.price_unit
#                     total = line.total_with_tax
#                     sub_total = line.price_subtotal
#                     for v in line.tax_id:
#                         tax.append(v.id)
#                     
#                     invoice_line_obj.create(cr, uid, 
#                                                     {
#                                                      'invoice_id' : invoice_id,
#                                                      'product_id' : product_id,
#                                                      'price_unit' : unit_price,
#                                                      'quantity' : pro_qty,
#                                                      'invoice_line_tax_id' : [(6, 0, tax)],
#                                                      'account_id' : line_account_id,
#                                                      'name' : desc,
#                                                      })
#                 invoice_obj.button_reset_taxes(cr, uid, [invoice_id])
#         return True
    
    
    


    