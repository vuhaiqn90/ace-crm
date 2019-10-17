from odoo import fields,models,api
from odoo.exceptions import UserError
import time
from datetime import datetime
from odoo.tools.translate import _

def get_price(self,pricelist_ids,price):
    price_amt=0.0
    pricelist_item_ids=[]
    if self._context is None:
        self._context = {}

    date = time.strftime('%Y-%m-%d')
    if 'date' in self._context:
        date = self._context['date']
                    
    currency_obj = self.env['res.currency']
    product_pricelist_version_obj = self.env['product.pricelist.item']
    user_browse = self.env['res.users'].browse(self._uid)
    company_obj = self.env['res.company']
    company_id = user_browse.company_id
    pricelist_obj=self.env['product.pricelist'].browse(pricelist_ids)
    if pricelist_ids:
        pricelist_item_ids.append(pricelist_ids)
        
    pricelist_item_ids=list(set(pricelist_item_ids))
    plversions_search_args = [
        ('pricelist_id', 'in', pricelist_item_ids),
        '|',
        ('date_start', '=', False),
        ('date_start', '<=', date),
        '|',
        ('date_end', '=', False),
        ('date_end', '>=', date),
    ]
    plversion_ids = product_pricelist_version_obj.search(plversions_search_args)
    if len(pricelist_item_ids) != len(plversion_ids):
        msg = "At least one pricelist has no active version !\nPlease create or activate one."
        raise Warning(_('Warning !'), _(msg))
    
    self._cr.execute(
                'SELECT i.* '
                'FROM product_pricelist_item AS i '
                'WHERE id = '+str(plversion_ids[0].id)+'')
    
    res1 = self._cr.dictfetchall()
    if pricelist_obj:
        price=company_id.currency_id.compute(price, pricelist_obj.currency_id, round=False)
    for res in res1:
        if res:
            price_limit = price
            price = price * (1.0+(res['price_discount'] or 0.0))
            price += (res['price_surcharge'] or 0.0)
            if res['price_min_margin']:
                price = max(price, price_limit+res['price_min_margin'])
            if res['price_max_margin']:
                price = min(price, price_limit+res['price_max_margin'])
            break

    price_amt = price
    return price_amt


class document_management(models.Model):
    _name = "document.management"
    _description = "Documents Management For Tours and Travel Services"

    name = fields.Char("Name",size=50,required=True)
    description = fields.Char('Description',size=164,required=True)
    

class service_scheme(models.Model):
    _name = "service.scheme"
    _description = "SCHEMES For Tours and Travel Services"

    name = fields.Char("Name",size=50,required=True)
    duration = fields.Char('Duration In Days',size=164,required=True)
    service_cost = fields.Float('Service Cost',size=164,required=True)

    

class passport_booking(models.Model):
    _name = "passport.booking"
    
    _description = "Passport  booking class "
    
    def get_partner_lang_date(self,date1,lang):       
        search_id = self.env['res.lang'].search([('code','=',lang)])
        record=search_id
        new_date=datetime.strftime(datetime.strptime(str(date1),'%Y-%m-%d'),record.date_format)
        return new_date
    
    
    @api.model
    def create(self, vals): 
        # function overwrites create method and auto generate request no. 
        req_no = self.env['ir.sequence'].get('passport.booking123')
        print(req_no)
        vals['name'] = req_no
        return super(passport_booking, self).create(vals)
    
    
    name = fields.Char("Name",size=50,readonly=True)
    current_date = fields.Date("Date",required=True,readonly=True, states={'draft': [('readonly', False)]})
    customer_id = fields.Many2one('res.partner','Customer',required=True,readonly=True, states={'draft': [('readonly', False)]})
#                'address_id':fields.many2one('res.partner.address','Customer Address',required=True,readonly=True, states={'draft': [('readonly', False)]}),
    email_id = fields.Char('Email Id',size=150,readonly=True, states={'draft': [('readonly', False)]})
    mobile = fields.Char('Mobile Number',size=64,readonly=True, states={'draft': [('readonly', False)]})
    product_id = fields.Many2one('product.product','Service',required=True,readonly=True, states={'draft': [('readonly', False)]})
    scheme_id = fields.Many2one('service.scheme','Service Scheme',required=True,readonly=True, states={'draft': [('readonly', False)]})
    document_line_ids = fields.One2many('passport.document.line','passport_book_id','Document Line',readonly=True, states={'draft': [('readonly', False)],'confirm': [('readonly', False)],'verify': [('readonly', False)]})
    attachment_line_ids = fields.One2many('ir.attachment','pass_book_id','Attachment Lines',readonly=True, states={'draft': [('readonly', False)],'confirm': [('readonly', False)],'verify': [('readonly', False)]})
    passport_invoice_ids = fields.Many2many('account.invoice','passport_invoice_rel', 'passport_book_id', 'invoice_id', 'Passport Invoices',readonly=True)
    service_charge = fields.Float('Service Cost',required=True,readonly=True, states={'draft': [('readonly', False)]})
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist',required=True,readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
                            ('draft', 'Draft'),
                            ('confirm', 'Confirm'),
                            ('verify', 'Verify Document'),
                            ('approve', 'Approved'),
                            ('invoice', 'Invoiced'),
                            ('in_process', 'In Process'),
                            ('done', 'Done'),
                            ('cancel', 'Canceled'),
                            ], 'Status',readonly=True,default=lambda *a: 'draft',)
                            
    
#     _defaults = {
#                  'state': lambda *a: 'draft',
#                  }
    
    def button_cancel(self):
        self.write({'state':'cancel'})
        return True
    
    
    @api.onchange('pricelist_id','scheme_id')
    def on_change_pricelist(self):
        res={}
        if self.pricelist_id and self.scheme_id:
            service_charge = self.scheme_id.service_cost
            service_charge = get_price(self, self.pricelist_id.id, service_charge)
            res['service_charge']=service_charge
        return {'value':res}
    
    
    @api.onchange('customer_id')
    def on_change_customer_id(self):
        result = {}
        invoice_addr_id = False
        if self.customer_id:
            res = self.customer_id.address_get(['delivery', 'invoice', 'contact'])
            if res['invoice']:
                invoice_addr_id = res['invoice']
            else:
                invoice_addr_id = res['contact']
            obj = self.customer_id
            if obj.email:
                result['email_id'] = obj.email
            if obj.mobile:
                result['mobile'] = obj.mobile
            result['address_id'] = invoice_addr_id
        return {'value': result}
      
    
    def button_confirm(self):
        return self.write({'state':'confirm'})
    
    
    def verify_document(self):
        for obj in self:
            if not obj.attachment_line_ids:
                raise UserError("Documents not verified. Please verify documents and make attachment")
            
        return self.write({'state':'verify'})
    
    
    def approve_document(self):
        for obj in self:
            if not obj.attachment_line_ids:
                raise UserError("Documents not verified. Please verify documents and make attachment")
            
        return self.write({'state':'approve'})
    
    
    def create_invoice(self):
        fiscal_position=False
        for obj in self:
            acc_id = obj.customer_id.property_account_receivable_id.id
            journal_obj = self.env['account.journal']
            journal_ids = journal_obj.search([('type', '=','sale')], limit=1)
            type = 'out_invoice' 
            inv = {
                    'name': obj.name,
                    'origin': obj.name,
                    'type': type,
                    'date_invoice':obj.current_date,
                    'reference': "Passport Booking",
                    'account_id': acc_id,
                    'partner_id': obj.customer_id.id,
#                    'address_invoice_id': address_invoice_id[0] or False,
                    'currency_id': obj.pricelist_id.currency_id.id,
                    'journal_id': len(journal_ids) and journal_ids[0].id or False,
                    'amount_total':obj.service_charge,
                    }
            inv_id = self.env['account.invoice'].create(inv)
            account_id = obj.product_id.property_account_income_id.id
            if not account_id:
                account_id = obj.product_id.categ_id.property_account_income_categ_id.id
            if not account_id:
                raise UserError(_('Error !'),
                        _('There is no income account defined ' \
                                'for this product: "%s" (id:%d)') % \
                                (obj.product_id.name, obj.product_id.id,))
            il = {
                    'product_id': obj.product_id.id,
                    'name': obj.product_id.name,
                    'account_id': account_id,
                    'price_unit':obj.service_charge , 
                    'quantity': 1.0,
                    'uos_id':  False,
                    'origin':obj.name,
                    'invoice_id':inv_id.id,
                    'product_id':obj.product_id.id,
                    'pay_date':obj.current_date,
                    'order_amt':obj.service_charge,
                    }
            invoice_line=self.env['account.invoice.line'].create(il)
            self._cr.execute('insert into passport_invoice_rel(passport_book_id,invoice_id) values (%s,%s)', (obj.id, inv_id.id))
            fpos = fiscal_position and self.env['account.fiscal.position'].browse(fiscal_position) or False
            tax_id = self.env['account.fiscal.position'].map_tax(obj.product_id.taxes_id)
            if tax_id:
                for txid in tax_id:
                    self._cr.execute('insert into account_invoice_line_tax(invoice_line_id,tax_id) values (%s,%s)', (invoice_line.id, txid.id))
        self.write({'state':'invoice'})
        return True
    
    
    def send_to_process(self):
        for obj in self:
            if obj.passport_invoice_ids[0].state != 'paid':
                raise Warning(_("Warning"),_("Invoice Is Not Paid Yet. Please Pay The Invoice Amount"))
        return self.write({'state':'in_process'})
    
    
    def issue_passport(self):
        for obj in self:
            if not obj.attachment_line_ids:
                raise Warning(_("Warning"),_("Documents not verified. Please verify documents and make attachment"))
        return self.write({'state':'done'})
    


class passport_document_line(models.Model):
    _name = "passport.document.line"
    _description = "Passport document line"

    document_type_id = fields.Many2one('document.management','Document Type',required=True)
    name = fields.Char("Xerox Copy/Photo Copy",size=50,required=True)
    original_copy = fields.Integer("Original Copy",size=50,default=1)
    passport_book_id = fields.Many2one('passport.booking','Passport Booking ID')

#     _defaults = {
#                  'original_copy': 1,
#                  }
    


class ir_attachment(models.Model):
    _inherit = "ir.attachment"
    _description = "Attachments Inherit For Passport Services"

    pass_book_id = fields.Many2one('passport.booking','Passport Book ID')
    
