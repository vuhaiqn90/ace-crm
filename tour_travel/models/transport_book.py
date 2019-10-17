import time
from odoo import fields,models,api
from odoo.tools.translate import _
from datetime import datetime, timedelta,time
from odoo.exceptions import UserError,Warning


def get_price(self,pricelist_ids,price):
    price_amt=0.0
    pricelist_item_ids=[]
    if self._context is None:
        self._context = {}

    date = datetime.strftime('%Y-%m-%d')
    if 'date' in self._context:
        date = self._context['date']

    currency_obj = self.env['res.currency']
    product_pricelist_version_obj = self.env['product.pricelist.item']
    user_browse = self.env['res.users'].browse(self._uid)
    company_id = user_browse.company_id.id
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
    if not plversion_ids:
        msg = 'Product pricelist item does not exists'
        raise Warning(msg)
    
    self._cr.execute(
                'SELECT i.* '
                'FROM product_pricelist_item AS i '
                'WHERE id = ' + str(plversion_ids[0].id) + '')
                
    res1 = self._cr.dictfetchall()
    if pricelist_obj:
        price=currency_obj.compute(price,pricelist_obj.currency_id.id, round=False)
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

    price_amt=price
    return price_amt

# def get_price(self,cr, uid, ids, pricelist_ids,price,context=None):
#     price_amt=0.0
#     pricelist_item_ids=[]
#     if context is None:
#         context = {}
# 
#     date = time.strftime('%Y-%m-%d')
#     if 'date' in context:
#         date = context['date']
#                     
#     currency_obj = self.pool.get('res.currency')
#     product_pricelist_version_obj = self.pool.get('product.pricelist.item')
#     user_browse = self.pool.get('res.users').browse(cr,uid,uid)
#     company_obj = self.pool.get('res.company')
#     company_id = company_obj.browse(cr,uid,user_browse.company_id.id)
#     pricelist_obj=self.pool.get('product.pricelist').browse(cr,uid,pricelist_ids)
#     if pricelist_ids:
#         pricelist_item_ids.append(pricelist_ids)
#         pricelist_obj=self.pool.get('product.pricelist').browse(cr,uid,pricelist_ids)
#         
#     pricelist_item_ids=list(set(pricelist_item_ids))
#     plversions_search_args = [
#         ('pricelist_id', 'in', pricelist_item_ids),
#         '|',
#         ('date_start', '=', False),
#         ('date_start', '<=', date),
#         '|',
#         ('date_end', '=', False),
#         ('date_end', '>=', date),
#     ]
# 
#     plversion_ids = product_pricelist_version_obj.search(cr, uid, plversions_search_args)
#     if not plversion_ids:
#         msg = 'Product pricelist item does not exists'
#         raise osv.except_osv(_('Warning !'), _(msg))
#     
#     cr.execute(
#                 'SELECT i.* '
#                 'FROM product_pricelist_item AS i '
#                 'WHERE id = ' + str(plversion_ids[0]) + '')
#                 
#     res1 = cr.dictfetchall()
#     if pricelist_obj:
#         price=currency_obj.compute(cr, uid, company_id.currency_id.id, pricelist_obj.currency_id.id, price, round=False)
#     for res in res1:
#         if res:
#             price_limit = price
#             price = price * (1.0+(res['price_discount'] or 0.0))
#             price += (res['price_surcharge'] or 0.0)
#             if res['price_min_margin']:
#                 price = max(price, price_limit+res['price_min_margin'])
#             if res['price_max_margin']:
#                 price = min(price, price_limit+res['price_max_margin'])
#             break
# 
#     price_amt=price
#     return price_amt


class transport_carrier(models.Model):
    _name = 'transport.carrier'
    _description = 'Transport Carrier'
    
    
    name = fields.Char('Carrier Name',size=128,required=True)
    code = fields.Char('Code',size=64)


class transport_information(models.Model):
    _name = "transport.information"
    _description = "Transport Information "
   
    name = fields.Char("Name",size=50,required=True)
    transport_recv_acc = fields.Many2one(
                            'account.account',
                            string="Receivable Account",
                            required=False
                    )
    transport_payble_acc = fields.Many2one(
                            'account.account',
                            string="Payable Account",
                            required=False
                                    )
    partner_id = fields.Many2one('res.partner',"Service Provider",required=True)
    transport_type_info_ids = fields.One2many('transport.type.info',"transport_id","Transport Information")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('done', 'Not Available')], 'Status',default=lambda *a:'draft')

    
    _sql_constraints = [
        ('partner_id_uniq', 'unique (partner_id)', 'You can not create more then one transport information for the same Partner !'),
    ]
    
#     _defaults = {
#                  'state': lambda *a:'draft',
#                  }
    
    @api.onchange('partner_id')
    def on_change_partner_id(self):
        result = {}
        invoice_addr_id = False
        if self.partner_id:
            res = self.partner_id.address_get(['delivery', 'invoice', 'contact'])
            if res['invoice']:
                invoice_addr_id = res['invoice']
            else:
                invoice_addr_id = res['contact']
            obj1 = self.partner_id
            result['name'] = obj1.name
        result['partner_addr_id'] = invoice_addr_id
        return {'value': result}



    @api.onchange('partner_id')
    def on_change_partner_id_one(self):
        if self.partner_id and not self.partner_id.property_account_receivable_id:
            raise Warning(' Please define customer account')
        self.transport_recv_acc=self.partner_id.property_account_receivable_id
        self.transport_payble_acc=self.partner_id.property_account_payable_id

    
    
#     def on_change_partner_id(self,cr,uid,ids,partner_id):
#         result = {}
#         invoice_addr_id = False
#         if partner_id:
#             res = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['delivery', 'invoice', 'contact'])
#             if res['invoice']:
#                 invoice_addr_id = res['invoice']
#             else:
#                 invoice_addr_id = res['contact']
#             obj1 = self.pool.get('res.partner').browse(cr,uid,partner_id)
#             result['name'] = obj1.name
#         result['partner_addr_id'] = invoice_addr_id
#         return {'value': result}
    
    def button_confirm(self):
        return self.write({'state':'confirm'})
    
#     def button_confirm(self, cr, uid, ids, context=None):
#         return self.write(cr, uid, ids, {'state':'confirm'})
    
    

class transport_type_info(models.Model):
    _name = "transport.type.info"
    _description = "Transport Type Information"
    
    name = fields.Char("Description",size=50,required=True)
    transport_type_id = fields.Many2one('product.product','Transport Type',required=True)
    transport_id = fields.Many2one('transport.information','Transport Info Ref',required=True)
    transport_carrier_id = fields.Many2one('transport.carrier','Carrier Name')
    cost_price = fields.Float("Cost Price(Adult)",required=True)
    sale_price = fields.Float("Sale Price(Adult)",required=True)
    cost_price_child = fields.Float("Cost Price(Child)",required=True)
    sale_price_child = fields.Float("Sale Price(Child)",required=True)
    from_destination_id = fields.Many2one('tour.destinations','From',required=True)
    to_destination_id = fields.Many2one('tour.destinations','To',required=True)
    from_date = fields.Date('From Date',required=True)
    to_date = fields.Date('To Date',required=True)
    travel_class_id = fields.Many2one('travel.class','Travel Class',required=True)
    
    _sql_constraints = [
        ('transport_id_details_uniq', 'unique (transport_id,transport_carrier_id, transport_type_id, travel_class_id, from_destination_id, to_destination_id, from_date, to_date )', 'The combination of From date, To date, Source to destination, Travel class and Service Provider must be unique !'),
    ]
    
    @api.onchange('transport_type_id')
    def on_change_transport_type_id(self):
        result = {}
        if self.transport_type_id:
            obj = self.transport_type_id
            result['name'] = obj.name
        return {'value': result}
    
#     def on_change_transport_type_id(self,cr,uid,ids,transport_type_id):
#         result = {}
#         if transport_type_id:
#             obj = self.pool.get('product.product').browse(cr,uid,transport_type_id)
#             result['name'] = obj.name
#         return {'value': result}
    



class transport_line(models.Model):
    _name = "transport.line"
    _description = "Transport Line"
    
    name = fields.Char("Name",size=50,required=True)
    transport_type_info_id = fields.Many2one('transport.type.info',"Transport Type")
    available_vehicle = fields.Float("Available Vehicles")
    required_vehicle = fields.Float("Required Vehicles")
    days_required = fields.Float("Number Of Days")
    vehicle_cost = fields.Float("Fare")
    total_price = fields.Float("Total Price")
    state = fields.Selection([
                               ('draft', 'Draft'),
                               ('book', 'Book'),
                               ('checked','Checked'),
                               ('cancel', 'Not Available'),
                               ('done', 'Done')
                               ], 'Status',readonly=True,default=lambda *a: 'draft')
    trasnport_line_id = fields.Many2one('transport.book','Transport book')
    
    
    @api.onchange('transport_type_info_id')
    def on_change_transport_type_info_id(self):
        result = {}
        trans_obj = self.transport_type_info_id
        result['name'] = trans_obj.name
        result['vehicle_cost'] = trans_obj.cost_price
        result['available_vehicle'] = trans_obj.available_vehicle
        return {'value': result}
    
#     def on_change_transport_type_info_id(self,cr,uid,ids,transport_type_info_id):
#         result = {}
#         trans_obj = self.pool.get('transport.type.info').browse(cr,uid,transport_type_info_id)
#         result['name'] = trans_obj.name
#         result['vehicle_cost'] = trans_obj.cost_price
#         result['available_vehicle'] = trans_obj.available_vehicle
#         return {'value': result}
    
    @api.depends('vehicle_cost','days_required')
    @api.onchange('required_vehicle')
    def on_change_required_vehicle(self):
        result = {}
        result['total_price'] = self.required_vehicle * self.vehicle_cost * self.days_required
        return {'value': result}
    
#     def on_change_required_vehicle(self,cr,uid,ids,required_vehicle,vehicle_cost,days_required):
#         result = {}
#         result['total_price'] = required_vehicle * vehicle_cost * days_required
#         return {'value': result}
    
    
    def check_availability(self):
        tot_room = 0
        for obj in self:
            tot_room = obj.transport_type_info_id.available_vehicle - obj.required_vehicle
            obj.transport_type_info_id.write({'available_vehicle':tot_room})
        self.write({'state':'book'})
        return True
    
#     def check_availability(self, cr, uid, ids, *args):
#         tot_room = 0
#         for obj in self.browse(cr,uid,ids):
#             tot_room = obj.transport_type_info_id.available_vehicle - obj.required_vehicle
#             self.pool.get('transport.type.info').write(cr, uid, obj.transport_type_info_id.id, {'available_vehicle':tot_room})
#         self.write(cr, uid, ids, {'state':'book'})
#         return True
    
#     _defaults = {
#                  'state': lambda *a: 'draft',
#                  }
        


class transport_book(models.Model):
    _name = "transport.book"
    _description = "Transport Booking"
    
    
    def get_partner_lang_date(self,date1,lang):       
        record = self.env['res.lang'].search([('code','=',lang)])
        new_datetime = ''
        print("date1---------------------------",date1,type(date1))
        date1=str(date1)
        print("date1 2----------------------------",date1,type(date1))
        if len(date1) > 11:
            print('Time')
            new_date=datetime.strftime(datetime.strptime(date1,'%Y-%m-%d %H:%M:%S'),record.date_format)
            new_time=datetime.strftime(datetime.strptime(date1,'%Y-%m-%d %H:%M:%S'),'%H:%M:%S')
            print('*Time',new_time)
            new_datetime = new_date + " " + new_time
        else:
            print('Date only')
            new_date=datetime.strftime(datetime.strptime(date1,'%Y-%m-%d'),record.date_format)
            new_datetime = new_date
        print("!!!!!!!!!!!!!!!!---new date=",new_datetime)        
        return new_datetime
    
#     def get_partner_lang_date(self, cr, uid, ids, date1,lang):       
#         search_id = self.pool.get('res.lang').search(cr,uid,[('code','=',lang)])
#         record=self.pool.get('res.lang').browse(cr,uid,search_id)
#         new_datetime = ''
#         if len(date1) > 11:
#             print('Time')
#             new_date=datetime.strftime(datetime.strptime(date1,'%Y-%m-%d %H:%M:%S'),record.date_format)
#             new_time=datetime.strftime(datetime.strptime(date1,'%Y-%m-%d %H:%M:%S'),'%H:%M:%S')
#             print('*Time',new_time)
#             new_datetime = new_date + " " + new_time
#         else:
#             print('Date only')
#             new_date=datetime.strftime(datetime.strptime(date1,'%Y-%m-%d'),record.date_format)
#             new_datetime = new_date
#         print("!!!!!!!!!!!!!!!!---new date=",new_datetime)        
#         return new_datetime
    
    
    @api.model
    def create(self,vals): 
        # function overwrites create method and auto generate request no. 
        req_no = self.env['ir.sequence'].get('transport.book')
        vals['name'] = req_no
        if 'mobile' in vals and 'address_id' in vals:
            address_browse = self.env['res.partner.address'].browse(vals['address_id'])
            if not address_browse.mobile:
                address_browse.write({'mobile':vals['mobile']})
        if 'email_id' in vals and 'address_id' in vals:
            address_browse = self.env['res.partner.address'].browse(vals['address_id'])
            if not address_browse.email:
                address_browse.write({'email':vals['email_id']})
        return super(transport_book, self).create(vals)
    
#     def create(self, cr, uid, vals, context=None): 
#         # function overwrites create method and auto generate request no. 
#         req_no = self.pool.get('ir.sequence').get(cr,uid,'transport.book'),
#         vals['name'] = req_no[0]
#         if vals.__contains__('mobile') and vals.__contains__('address_id'):
#             address_browse = self.pool.get('res.partner.address').browse(cr, uid, vals['address_id'])
#             if not address_browse.mobile:
#                 self.pool.get('res.partner.address').write(cr, uid, vals['address_id'], {'mobile':vals['mobile']})
#         if vals.__contains__('email_id') and vals.__contains__('address_id'):
#             address_browse = self.pool.get('res.partner.address').browse(cr, uid, vals['address_id'])
#             if not address_browse.email:
#                 self.pool.get('res.partner.address').write(cr, uid, vals['address_id'], {'email':vals['email_id']})
#         return super(transport_book, self).create(cr, uid, vals, context=context)
    
    
    
    def _get_total_amt_transport(self):
        res = {}
        val=0.0
        total = 0
        for obj in self:
            for i in range (0,len(obj.customer_line_ids)):
                price = 0.0
                if obj.customer_line_ids[i].type == 'adult':
                    price = obj.cost_price
                else:
                    price = obj.cost_price_child
                total += price
            val = obj._amount_transport_line_tax(total) #calculation tax amount for suppliter
            res[obj.id] = total + val
        return res
    
    
    
#     def _get_total_amt_transport(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         val=0.0
#         total = 0
#         for obj in self.browse(cr, uid, ids):
#             for i in range (0,len(obj.customer_line_ids)):
#                 price = 0.0
#                 if obj.customer_line_ids[i].type == 'adult':
#                     price = obj.cost_price
#                 else:
#                     price = obj.cost_price_child
#                 total += price
#             val = self._amount_transport_line_tax(cr, uid, obj, total, context=context) #calculation tax amount for suppliter
#             res[obj.id] = total + val
#         return res
    
    def _amount_transport_line_tax(self, total):
        val = 0.0
        tax = self.transport_type_id.supplier_taxes_id.compute_all(total, None, 1, self.customer_id)
        for c in tax['taxes']:
            val += c.get('amount', 0.0)
        print("supplier tax amount ",val)
        return val
    
    
#     def _amount_transport_line_tax(self, cr, uid, line,total, context=None):
#         val = 0.0
#         tax = line.transport_type_id.supplier_taxes_id.compute_all(total, None, 1, line.customer_id)
#         for c in tax['taxes']:
#             val += c.get('amount', 0.0)
#         print("supplier tax amount ",val)
#         return val
    
    
    def _get_total_amt(self):
        res = {}
        total = 0
        tax_amount = 0.0
        tax_amt = self._get_tax_amt()
        for t in tax_amt.values():
            tax_amount = t
        for obj in self:
            for i in range (0,len(obj.customer_line_ids)):
                price = 0.0
                if obj.customer_line_ids[i].type == 'adult':
                    price = obj.sale_price
                else:
                    price = obj.sale_price_child
                total += price
            res[obj.id] = total +  tax_amount
        return res
    
#     def _get_total_amt(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         total = 0
#         tax_amount = 0.0
#         tax_amt = self._get_tax_amt(cr, uid, ids, args1, args2, context)
#         for t in tax_amt.values():
#             tax_amount = t
#         for obj in self.browse(cr, uid, ids):
#             for i in range (0,len(obj.customer_line_ids)):
#                 price = 0.0
#                 if obj.customer_line_ids[i].type == 'adult':
#                     price = obj.sale_price
#                 else:
#                     price = obj.sale_price_child
#                 total += price
#             res[obj.id] = total +  tax_amount
#         return res
     
    
    def _amount_customer_line_tax(self):
        val = 0.0
        amount_cost = (self.adult * self.sale_price) + (self.child * self.sale_price_child)
        tax = self.tax_id.compute_all(amount_cost, None, 1, self.customer_id)
        for c in tax['taxes']:
            val += c.get('amount', 0.0)
        return val
    
#     def _amount_customer_line_tax(self, cr, uid, line, context=None):
#         val = 0.0
#         amount_cost = (line.adult * line.sale_price) + (line.child * line.sale_price_child)
#         tax = line.tax_id.compute_all(amount_cost, None, 1, line.customer_id)
#         for c in tax['taxes']:
#             val += c.get('amount', 0.0)
#         return val
    
    
    def _get_tax_amt(self):
        res={}
        val=0.0
        for obj in self:
            val = obj._amount_customer_line_tax()
            res[obj.id] = val
        return res
    
#     def _get_tax_amt(self,cr,uid,ids,args1,args2,context=None):
#         res={}
#         val=0.0
#         for obj in self.browse(cr, uid, ids):
#             val = self._amount_customer_line_tax(cr, uid, obj, context=context)
#             res[obj.id] = val
#         return res
    
    def _get_untax_amt(self):
        res = {}
        total = 0
        for obj in self:
            for i in range (0,len(obj.customer_line_ids)):
                price = 0.0
                if obj.customer_line_ids[i].type == 'adult':
                    price = obj.sale_price
                else:
                    price = obj.sale_price_child
                total += price
            res[obj.id] = total
        return res
    
#     def _get_untax_amt(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         total = 0
#         for obj in self.browse(cr,uid,ids):
#             for i in range (0,len(obj.customer_line_ids)):
#                 price = 0.0
#                 if obj.customer_line_ids[i].type == 'adult':
#                     price = obj.sale_price
#                 else:
#                     price = obj.sale_price_child
#                 total += price
#             res[obj.id] = total
#         return res 
    
#    def write(self, cr, uid, ids, vals, context=None):
#        """
#        write method is override to get correct value of "max_dummy" field
#        """
#        for obj in self.browse(cr, uid, ids):
#            print obj,"fkfkjfjkfgj"
#            if vals.__contains__('mobile') and vals.__contains__('address_id'):
#                address_browse = self.pool.get('res.partner.address').browse(cr, uid, vals['address_id'])
#                if not address_browse.mobile:
#                    self.pool.get('res.partner.address').write(cr, uid, vals['address_id'], {'mobile':vals['mobile']})
#            if vals.__contains__('mobile') and obj.address_id:
#                 address_browse = self.pool.get('res.partner.address').browse(cr, uid, obj.address_id.id)
#                 if not address_browse.mobile:
#                    self.pool.get('res.partner.address').write(cr, uid, obj.address_id.id, {'mobile':vals['mobile']})
#            if vals.__contains__('email_id') and vals.__contains__('address_id'):
#                address_browse = self.pool.get('res.partner.address').browse(cr, uid, vals['address_id'])
#                if not address_browse.email:
#                    self.pool.get('res.partner.address').write(cr, uid, vals['address_id'], {'email':vals['email_id']})
#            if vals.__contains__('email_id') and obj.address_id:
#                 address_browse = self.pool.get('res.partner.address').browse(cr, uid, obj.address_id.id)
#                 if not address_browse.email:
#                    self.pool.get('res.partner.address').write(cr, uid, obj.address_id.id, {'email':vals['email_id']})
#        return super(transport_book, self).write(cr, uid, ids, vals, context=context)
    
    name = fields.Char("Registration ID",size=50,readonly=True)
    current_date = fields.Date("Booking Date")
    checkin_date = fields.Date("Journey Date",readonly=True, states={'draft': [('readonly', False)]})
    customer_id = fields.Many2one('res.partner','Customer',required=True,readonly=True,states={'draft': [('readonly', False)]})
    email_id = fields.Char('Email Id',size=150,readonly=True,states={'draft': [('readonly', False)]})
    mobile = fields.Char('Mobile', size=64,required=True,readonly=True,states={'draft': [('readonly', False)]})
    transport_id = fields.Many2one('transport.information',string="Transport Company",required=True,readonly=True,states={'draft': [('readonly', False)]})
    transport_reserve_invoice_ids = fields.Many2many('account.invoice','transport_reserve_invoice_rel', 'transport_book_id', 'invoice_id', 'Room Reservation Invoices',readonly=True)
    tax = fields.Integer("Tax")
    transport_line_ids = fields.One2many('transport.line',"trasnport_line_id",string="Transport Line")
    tax_id = fields.Many2many('account.tax', 'transport_book_tax', 'transport_type_id', 'tax_id', string='Taxes', readonly=True, states={'draft':[('readonly',False)]})   
#     tax_amt = fields.Float(compute=_get_tax_amt, string="Taxes ", store=True)
#     total_amt = fields.Float(compute=_get_total_amt,string="Customer Invoice Amount", store=True,help="This fields shows Amount as per the currency of selected pricelist at header.")
#     untax_amt = fields.Float(compute=_get_untax_amt,string="Untaxed Amount", store=True)
    untax_amt = fields.Float(compute='onchange_transport_room_reserve_supplier_invoice_ids',string="Untaxed Amount",store=True)
    tax_amt = fields.Float(compute='onchange_transport_room_reserve_supplier_invoice_ids',string="Taxes ", store=True)
    total_amt = fields.Float(compute='onchange_transport_room_reserve_supplier_invoice_ids',string="Customer Invoice Amount", store=True,help="This fields shows Amount as per the currency of selected pricelist at header.")
    total_amt_transport = fields.Float(string="Transport Invoice Amount", store=True,help="This fields shows Amount as per the currency of selected pricelist at header..However, supplier invoice shall be raise based on the currency of pricelist linked with supplier.")
    arrival_date = fields.Datetime("Arrival Date",help="This is an Arrival date and time of a carrier at Boarding station",states={'invoiced': [('readonly', True)],'book': [('readonly', True)],'done': [('readonly', True)],'issue': [('readonly', True)]})
    depart_date = fields.Datetime("Departure Date",help="This is an Departure date and time of a carrier at Boarding station",states={'invoiced': [('readonly', True)],'book': [('readonly', True)],'done': [('readonly', True)],'issue': [('readonly', True)]})
    transport_room_reserve_supplier_invoice_ids = fields.Many2many('account.invoice','transport_room_reserve_supplier_invoice_rel', 'transport_book_id', 'invoice_id', 'Transport Room Reservation Invoices',readonly=True)
    pnr_no = fields.Char("PNR No",size=50,states={'invoiced': [('readonly', True)],'book': [('readonly', True)],'done': [('readonly', True)],'issue': [('readonly', True)]})
    carrier_id = fields.Char("Carrier No",size=50,states={'invoiced': [('readonly', True)],'book': [('readonly', True)],'done': [('readonly', True)],'issue': [('readonly', True)]})
    tour_id = fields.Many2one("tour.package","Tour",readonly=True)
    tour_book_id = fields.Many2one("tour.booking","Tour Booking Ref",readonly=True)
    start_date = fields.Many2one('tour.dates',"Tour Start Date",readonly=True)
    adult = fields.Integer("Adult Persons",readonly=True, required=True,states={'draft': [('readonly', False)]})
    child = fields.Integer("Child",readonly=True,required=True, states={'draft': [('readonly', False)]})
    transport_type_id = fields.Many2one('product.product','Transport Type',required=True,readonly=True,states={'draft': [('readonly', False)]})
    transport_carrier_id = fields.Many2one('transport.carrier','Carrier Name',readonly=True,states={'draft': [('readonly', False)]})
    cost_price = fields.Float("Cost Price(Adult)")# readonly=True, states={'draft': [('readonly', False)]}
    sale_price = fields.Float("Sale Price(Adult)")
    cost_price_child = fields.Float("Cost Price(Child)")
    sale_price_child = fields.Float("Sale Price(Child)")
    from_destination_id = fields.Many2one('tour.destinations','From',required=True,readonly=True,states={'draft': [('readonly', False)]})
    to_destination_id = fields.Many2one('tour.destinations','To',required=True,readonly=True,states={'draft': [('readonly', False)]})
    travel_class_id = fields.Many2one('travel.class','Travel Class',required=True,readonly=True,states={'draft': [('readonly', False)]})
    customer_line_ids = fields.One2many('tour.customer.details',"customer_id","Transport Line",states={'done': [('readonly', True)]})
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist',required=True,readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
                           ('draft', 'Draft'),
                           ('confirm', 'Confirm'),
                           ('request', "Waiting For Transporter Approval"),
                           ('approve', 'Approved'),
                           ('invoiced', "Invoiced"),
                           ('issue', "Ticket Issue"),
                           ('done', 'Done'),
                           ('cancel', 'Canceled'),
                           ], 'Status',readonly=True,default=lambda *a: 'draft')

    
#     _defaults = {
#                  'state': lambda *a: 'draft',
#                  'current_date':lambda *args: time.strftime('%Y-%m-%d'),
#                  }
    @api.multi
    def send_to_hotel(self):
        self.write({'state':'request'})
        return True
    
#     def send_to_hotel(self, cr, uid, ids, *args):
#         self.write(cr, uid, ids, {'state':'request'})
#         return True
    
    @api.multi
    def make_approval(self):
        self.write({'state':'approve'})
        return True
    
#     def make_approval(self, cr, uid, ids, *args):
#         self.write(cr, uid, ids, {'state':'approve'})
#         return True
    
    @api.multi
    def button_cancel(self):
        self.write({'state':'cancel'})
        return True
    
#     def button_cancel(self, cr, uid, ids, *args):
#         self.write(cr, uid, ids, {'state':'cancel'})
#         return True
    @api.multi
    @api.depends('state','transport_room_reserve_supplier_invoice_ids')
    def onchange_transport_room_reserve_supplier_invoice_ids(self):
        subtot=0
        tax_amt=0
        tot_amt=0
        print ("=============================")
        for rec in self.transport_room_reserve_supplier_invoice_ids:
            
            subtot+=rec.amount_untaxed
            tax_amt+=rec.amount_tax
            tot_amt+=rec.amount_total
            print (subtot)
        self.untax_amt = subtot
        self.tax_amt = tax_amt
        self.total_amt = tot_amt
        if self.state=='invoiced':
            self.tax_amt = tax_amt
            self.total_amt = tot_amt
            
        if self.state=='issue':
            self.tax_amt = tax_amt
            self.total_amt = tot_amt
        
        if self.state=='done':
            self.tax_amt = tax_amt
            self.total_amt = tot_amt
        
    @api.onchange('customer_id')
    def on_change_customer_id(self):
        result = {}
        if self.customer_id:
            result['email_id'] = self.customer_id.email
            result['mobile1'] = self.customer_id.mobile
        return {'value': result}
    
    @api.onchange('tour_sale_order_ids')
    def onchange_sale_order(self):
        subtot=0
        tax_amt=0
        tot_amt=0
        for rec in self.tour_sale_order_ids:
            
            subtot+=rec.amount_untaxed
            tax_amt+=rec.amount_tax
            tot_amt+=rec.amount_total
        
        self.untax_amt = subtot
        self.tax_amt = tax_amt
        self.total_amt = tot_amt
    
    @api.onchange('customer_id')
    def on_change_customer_id(self):
        result = {}
        invoice_addr_id = False
        if self.customer_id:
            res = self.customer_id.address_get(['delivery', 'invoice', 'contact'])
            invoice_addr_id = res['contact']
            obj1 = self.customer_id
            result['address_id'] = invoice_addr_id
            result['email_id'] = obj1.email
            result['mobile'] = obj1.mobile  
        return {'value': result}
    
    
#     def on_change_customer_id(self,cr,uid,ids,customer_id):
#         result = {}
#         invoice_addr_id = False
#         if customer_id:
#             res = self.pool.get('res.partner').address_get(cr, uid, [customer_id], ['delivery', 'invoice', 'contact'])
#             invoice_addr_id = res['contact']
#             obj1 = self.pool.get('res.partner').browse(cr,uid,customer_id)
#             result['address_id'] = invoice_addr_id
#             result['email_id'] = obj1.email
#             result['mobile'] = obj1.mobile  
#         return {'value': result}
    
    
    @api.depends('current_date','transport_carrier_id', 'transport_type_id', 'travel_class_id', 'from_destination_id', 'to_destination_id','pricelist_id')
    @api.onchange('transport_id')
    def on_change_transport_details(self):
        result = {}
        warning = {}
        print("on_change_transport_details")
        if (self.transport_id and self.current_date and self.transport_carrier_id and self.transport_type_id and self.travel_class_id and self.from_destination_id and self.to_destination_id and self.pricelist_id):
            print("ssss")
            res = self.transport_id
            res_product = self.transport_type_id
            tax_list = []
            for tax in res_product.taxes_id:
                tax_list.append(tax.id)
            result['tax_id'] = [(6,0,tax_list)]
            if res.transport_type_info_ids:
                result['cost_price'] = 0.00
                result['sale_price'] = 0.00
                result['cost_price_child'] = 0.00
                result['sale_price_child'] = 0.00
                for line in res.transport_type_info_ids:
                    if (line.from_date <= self.current_date and self.current_date <= line.to_date and line.transport_carrier_id.id == self.transport_carrier_id and
                        line.transport_type_id.id == self.transport_type_id and line.travel_class_id.id == self.travel_class_id and 
                        line.from_destination_id.id == self.from_destination_id and line.to_destination_id.id == self.to_destination_id):
                        result['cost_price'] = get_price(self, self.pricelist_id.id, line.cost_price)
                        result['sale_price'] = get_price(self, self.pricelist_id.id, line.sale_price)
                        result['cost_price_child'] = get_price(self, self.pricelist_id.id, line.cost_price_child)
                        result['sale_price_child'] = get_price(self, self.pricelist_id.id, line.sale_price_child)
                        
                if not (result['cost_price'] or result['sale_price'] or result['cost_price_child'] or result['sale_price_child']):
                    warn_msg = _("Rate is not define for above transport information.") 
                    warning = {
                        'title': _('Warning !'),
                        'message': warn_msg
                        }
            else:
                warn_msg = _("Rate is not define for above transport information.")
                warning = {
                    'title': _('Warning !'),
                    'message': warn_msg
                    }
        print(result,"result",warning,"warning ")
        return {'value': result,'warning': warning }
    
#     def on_change_transport_details(self, cr, uid, ids, transport_id, current_date, transport_carrier_id, transport_type_id, travel_class_id, from_destination_id, to_destination_id,price_list):
#         result = {}
#         warning = {}
#         print("on_change_transport_details")
#         if (transport_id and current_date and transport_carrier_id and transport_type_id and travel_class_id and from_destination_id and to_destination_id and price_list):
#             print("ssss")
#             pricelist_id = self.pool.get('product.pricelist').browse(cr,uid,price_list)
#             res = self.pool.get('transport.information').browse(cr, uid, transport_id)
#             res_product = self.pool.get('product.product').browse(cr, uid, transport_type_id)
#             tax_list = []
#             for tax in res_product.taxes_id:
#                 tax_list.append(tax.id)
#             result['tax_id'] = [(6,0,tax_list)]
#             if res.transport_type_info_ids:
#                 result['cost_price'] = 0.00
#                 result['sale_price'] = 0.00
#                 result['cost_price_child'] = 0.00
#                 result['sale_price_child'] = 0.00
#                 for line in res.transport_type_info_ids:
#                     if (line.from_date <= current_date and current_date <= line.to_date and line.transport_carrier_id.id == transport_carrier_id and
#                          line.transport_type_id.id == transport_type_id and line.travel_class_id.id == travel_class_id and 
#                          line.from_destination_id.id == from_destination_id and line.to_destination_id.id == to_destination_id):
#                         result['cost_price'] = get_price(self, cr, uid, ids, pricelist_id.id, line.cost_price)
#                         result['sale_price'] = get_price(self, cr, uid, ids, pricelist_id.id, line.sale_price)
#                         result['cost_price_child'] = get_price(self, cr, uid, ids, pricelist_id.id, line.cost_price_child)
#                         result['sale_price_child'] = get_price(self, cr, uid, ids, pricelist_id.id, line.sale_price_child)
#                         
#                 if not (result['cost_price'] or result['sale_price'] or result['cost_price_child'] or result['sale_price_child']):
#                     warn_msg = _("Rate is not define for above transport information.") 
#                     warning = {
#                         'title': _('Warning !'),
#                         'message': warn_msg
#                         }
#             else:
#                 warn_msg = _("Rate is not define for above transport information.")
#                 warning = {
#                     'title': _('Warning !'),
#                     'message': warn_msg
#                     }
#         print(result,"result",warning,"warning ")
#         return {'value': result,'warning': warning }
    
    
    def compute_amt(self):
        for obj in self:
            if not (obj.cost_price and obj.sale_price and obj.cost_price_child and obj.sale_price_child):
                raise Warning("Rate is not define for above transport information.")
        return True
    
    
#     def compute_amt(self, cr, uid, ids, *args):
#         for obj in self.browse(cr,uid,ids):
#             if not (obj.cost_price and obj.sale_price and obj.cost_price_child and obj.sale_price_child):
#                 raise osv.except_osv(_("Warning"),_("Rate is not define for above transport information."))
#         return True
    
    def get_price_for_invoice(self):
        subtot=0
        tax_amt=0
        tot_amt=0
        print ("=============================")
        for rec in self.transport_room_reserve_supplier_invoice_ids:
            
            subtot+=rec.amount_untaxed
            tax_amt+=rec.amount_tax
            tot_amt+=rec.amount_total
            #print (rec.name)
        self.untax_amt = subtot
        self.tax_amt = tax_amt
        self.total_amt = tot_amt
        
    
    def create_invoice(self):
        for obj in self:
            if not (obj.pnr_no and obj.carrier_id and obj.arrival_date and obj.depart_date):
                raise Warning("Please fill all required Tour Information.")
            if obj.tour_id:
                tot_days = int(obj.tour_id.days)
                st_dt = str(obj.start_date.start_date).split(' ')[0]
                print (st_dt,'\n\n')
                
                dt_from =obj.start_date.start_date
                single_date = str(dt_from + timedelta(days=tot_days))
                single_date=datetime.strptime(single_date,'%Y-%m-%d').date()
#                 obj.start_date.start_date=datetime.strptime(obj.start_date.start_date,'%Y-%m-%d %H:%M:%S')
#                                   datetime.combine(d, datetime.min.time())
                if (obj.arrival_date.date() < obj.start_date.start_date or obj.arrival_date.date() > single_date):
                    raise Warning("You are giving wrong arrival date.")
                if (obj.depart_date.date()< obj.start_date.start_date or obj.depart_date.date() > single_date):
                    raise Warning("You are giving wrong departure date.")
            for customer in obj.customer_line_ids:
                if not customer.room_no:
                    raise Warning("Seat / Berth No. is not assign to customer.")
            if not obj.tour_id:
                acc_id = obj.customer_id.property_account_receivable_id.id
                     
                journal_ids = self.env['account.journal'].search([('type', '=','sale')], limit=1)
                type1 = 'out_invoice' 
                inv = {
                            'name': obj.name,
                            'origin': obj.name,
                            'type': type1,
                            'reference': "Transport Reservation",
                            'account_id': acc_id,
                            'partner_id': obj.customer_id.id,
                            'currency_id': obj.pricelist_id.currency_id.id,
                            'journal_id': len(journal_ids) and journal_ids[0].id or False,
                            'amount_tax':obj.tax_amt,
                            'amount_untaxed':obj.untax_amt,
                            'amount_total':obj.total_amt,
                            }
                print("inv",inv)
                inv_id = self.env['account.invoice'].create(inv)
                print("tax_id",obj.tax_id)
                tax = []
                for i in obj.tax_id:
                    tax.append(i.id)
                account_id = obj.transport_type_id.property_account_income_id.id
                if not account_id:
                    account_id = obj.transport_type_id.categ_id.property_account_income_categ_id.id
                if not account_id:
                    raise UserError('There is no income account defined ' \
                                    'for this product: "%s" (id:%d)' % \
                                    (obj.transport_type_id.name, obj.transport_type_id.id))
                il = {
                        'name': obj.transport_type_id.name + '( Ticket )' or obj.name,
                        'product_id':obj.transport_type_id.id,
                        'account_id': account_id,
                        'price_unit':obj.untax_amt , 
                        'quantity': 1.0,
                        'uos_id':  False,
                        'origin':obj.name,
                        'invoice_id':inv_id.id,
                        'pay_date':obj.current_date,
                        'order_amt':obj.untax_amt,
                        'invoice_line_tax_id':[(6,0,tax)],
                        }
                print("il",il)
                self.env['account.invoice.line'].create(il)
                self._cr.execute('insert into transport_reserve_invoice_rel(transport_book_id,invoice_id) values (%s,%s)', (obj.id, inv_id.id))
            
            acc_id = obj.transport_id.partner_id.property_account_payable_id.id
            
            journal_ids = self.env['account.journal'].search([('type', '=','purchase')], limit=1)
            line_account_id = obj.transport_type_id.property_account_expense_id.id
            if not line_account_id:
                line_account_id = obj.transport_type_id.categ_id.property_account_expense_categ_id.id
            if not line_account_id:
                raise UserError('There is no income account defined ' \
                                'for this product: "%s" (id:%d)' % \
                                (obj.transport_type_id.name, obj.transport_type_id.id))
            if not obj.transport_id.partner_id.property_product_pricelist:
                raise Warning("Price list is not define for Transport Partner.")
            tax_amount = self.get_price_for_invoice()
            untax_amount = self.get_price_for_invoice()
            total_transport_amount = self.get_price_for_invoice()
            
            type1 = 'in_invoice' 
            inv = {
                    'name': obj.name,
                    'origin': obj.name,
                    'type': type1,
                    'reference': "Transport Reservation Invoice",
                    'account_id': acc_id,
                    'partner_id': obj.transport_id.partner_id.id,
                    'currency_id': obj.transport_id.partner_id.property_product_pricelist.id,
                    'journal_id': len(journal_ids) and journal_ids[0].id or False,
                    'amount_tax':tax_amount,
                    'amount_untaxed':untax_amount,
                    'amount_total':total_transport_amount,
                }
            inv_id = self.env['account.invoice'].create(inv)
            tax1 = []
            #All taxes on purchase get according to product            
            for i in obj.transport_type_id.supplier_taxes_id:
                tax1.append(i.id)
            il = {
                    'name': obj.transport_type_id.name + '( Ticket )' or obj.name,
                    'product_id':obj.transport_type_id.id,
                    'account_id': line_account_id,
                    'price_unit':total_transport_amount,
                    'quantity': 1.0,
                    'uos_id':  False,
                    'origin':obj.name,
                    'invoice_id':inv_id.id,
                    'pay_date':obj.current_date,
                    'order_amt':total_transport_amount,
                    'invoice_line_tax_id':[(6,0,tax1)],
                    }
            self.env['account.invoice.line'].create(il)
            self._cr.execute('insert into transport_room_reserve_supplier_invoice_rel(transport_book_id,invoice_id) values (%s,%s)', (obj.id, inv_id.id))
            
        self.write({'state':'invoiced'})
        return True
    
    
    
#     def create_invoice(self, cr, uid, ids, *args):
#         for obj in self.browse(cr,uid,ids):
#             if not (obj.pnr_no and obj.carrier_id and obj.arrival_date and obj.depart_date):
#                 raise osv.except_osv(_("Warning"),_("Please fill all required Tour Information."))
#             if obj.tour_id:
#                 tot_days = int(obj.tour_id.days)
#                 st_dt = obj.start_date.start_date.split(' ')[0],
#                 dt_from = mx.DateTime.strptime(st_dt[0], '%Y-%m-%d')
#                 single_date = str(dt_from + RelativeDateTime(days=tot_days))
#                 print("single_date",single_date[0:10])
#                 if (obj.arrival_date[0:10] < obj.start_date.start_date or obj.arrival_date[0:10] > single_date[0:10]):
#                     raise osv.except_osv(_("Warning"),_("You are giving wrong arrival date."))
#                 if (obj.depart_date[0:10] < obj.start_date.start_date or obj.depart_date[0:10] > single_date[0:10]):
#                     raise osv.except_osv(_("Warning"),_("You are giving wrong departure date."))
#             for customer in obj.customer_line_ids:
#                 if not customer.room_no:
#                     raise osv.except_osv(_("Warning"),_("Seat / Berth No. is not assign to customer."))
#             if not obj.tour_id:
#                 acc_id = obj.customer_id.property_account_receivable_id.id
#                      
#                 journal_obj = self.pool.get('account.journal')
#                 journal_ids = journal_obj.search(cr, uid, [('type', '=','sale')], limit=1)
#                 type = 'out_invoice' 
#                 inv = {
#                             'name': obj.name,
#                             'origin': obj.name,
#                             'type': type,
#                             'reference': "Transport Reservation",
#                             'account_id': acc_id,
#                             'partner_id': obj.customer_id.id,
#                             'currency_id': obj.pricelist_id.currency_id.id,
#                             'journal_id': len(journal_ids) and journal_ids[0] or False,
#                             'amount_tax':obj.tax_amt,
#                             'amount_untaxed':obj.untax_amt,
#                             'amount_total':obj.total_amt,
#                             }
#                 print("inv",inv)
#                 inv_id = self.pool.get('account.invoice').create(cr, uid, inv)
#                 print("tax_id",obj.tax_id)
#                 tax = []
#                 for i in obj.tax_id:
#                     tax.append(i.id)
#                 account_id = obj.transport_type_id.property_account_income_id.id
#                 if not account_id:
#                     account_id = obj.transport_type_id.categ_id.property_account_income_categ_id.id
#                 if not account_id:
#                     raise osv.except_osv(_('Error !'),
#                             _('There is no income account defined ' \
#                                     'for this product: "%s" (id:%d)') % \
#                                     (obj.transport_type_id.name, obj.transport_type_id.id,))
#                 il = {
#                         'name': obj.transport_type_id.name + '( Ticket )' or obj.name,
#                         'product_id':obj.transport_type_id.id,
#                         'account_id': account_id,
#                         'price_unit':obj.untax_amt , 
#                         'quantity': 1.0,
#                         'uos_id':  False,
#                         'origin':obj.name,
#                         'invoice_id':inv_id,
#                         'pay_date':obj.current_date,
#                         'order_amt':obj.untax_amt,
#                         'invoice_line_tax_id':[(6,0,tax)],
#                         }
#                 print("il",il)
#                 self.pool.get('account.invoice.line').create(cr, uid, il,)
#                 cr.execute('insert into transport_reserve_invoice_rel(transport_book_id,invoice_id) values (%s,%s)', (obj.id, inv_id))
#             
#             acc_id = obj.transport_id.partner_id.property_account_payable_id.id
#             
#             journal_obj = self.pool.get('account.journal')
#             journal_ids = journal_obj.search(cr, uid, [('type', '=','purchase')], limit=1)
#             line_account_id = obj.transport_type_id.property_account_expense_id.id
#             if not line_account_id:
#                 line_account_id = obj.transport_type_id.categ_id.property_account_expense_categ_id.id
#             if not line_account_id:
#                 raise osv.except_osv(_('Error !'),
#                         _('There is no income account defined ' \
#                                 'for this product: "%s" (id:%d)') % \
#                                 (obj.transport_type_id.name, obj.transport_type_id.id,))
#             if not obj.transport_id.partner_id.property_product_pricelist:
#                 raise osv.except_osv(_("Warning"),_("Price list is not define for Transport Partner."))
#             tax_amount = get_price(self, cr, uid, ids, obj.transport_id.partner_id.property_product_pricelist.id, obj.tax_amt)
#             untax_amount = get_price(self, cr, uid, ids, obj.transport_id.partner_id.property_product_pricelist.id, obj.untax_amt)
#             total_transport_amount = get_price(self, cr, uid, ids, obj.transport_id.partner_id.property_product_pricelist.id, obj.total_amt_transport)
#             
#             type = 'in_invoice' 
#             inv = {
#                         'name': obj.name,
#                         'origin': obj.name,
#                         'type': type,
#                         'reference': "Transport Reservation Invoice",
#                         'account_id': acc_id,
#                         'partner_id': obj.transport_id.partner_id.id,
#                         'currency_id': obj.transport_id.partner_id.property_product_pricelist.id,
#                         'journal_id': len(journal_ids) and journal_ids[0] or False,
#                         'amount_tax':tax_amount,
#                         'amount_untaxed':untax_amount,
#                         'amount_total':total_transport_amount,
#                         }
#             print("inv",inv)
#             inv_id = self.pool.get('account.invoice').create(cr, uid, inv)
#             tax1 = []
#             #All taxes on purchase get according to product            
#             for i in obj.transport_type_id.supplier_taxes_id:
#                 tax1.append(i.id)
#             il = {
#                     'name': obj.transport_type_id.name + '( Ticket )' or obj.name,
#                     'product_id':obj.transport_type_id.id,
#                     'account_id': line_account_id,
#                     'price_unit':total_transport_amount,
#                     'quantity': 1.0,
#                     'uos_id':  False,
#                     'origin':obj.name,
#                     'invoice_id':inv_id,
#                     'pay_date':obj.current_date,
#                     'order_amt':total_transport_amount,
#                     'invoice_line_tax_id':[(6,0,tax1)],
#                     }
#             print("il",il)
#             self.pool.get('account.invoice.line').create(cr, uid, il,)
#             cr.execute('insert into transport_room_reserve_supplier_invoice_rel(transport_book_id,invoice_id) values (%s,%s)', (obj.id, inv_id))
#             
#         self.write(cr, uid, ids, {'state':'invoiced'})
#         return True
    
    
    def issue_ticket(self):
        for obj in self:
            if not obj.tour_id:
                if obj.transport_room_reserve_supplier_invoice_ids[0].state !='paid':
                    raise Warning("Please Pay The Invoice Amount ")
            self.write({'state':'issue'})
        return True
    
#     def issue_ticket(self, cr, uid, ids, *args):
#         
#         for obj in self.browse(cr,uid,ids):
#             if not obj.tour_id:
#                 if obj.transport_room_reserve_supplier_invoice_ids[0].state !='paid':
#                     raise osv.except_osv(_("Warning"),_("Please Pay The Invoice Amount "))
#             self.write(cr, uid, ids, {'state':'issue'})
#         return True
    
    
    def make_done(self):
        for obj in self:
            self.write({'state':'done'})
        return True
    
#     def make_done(self, cr, uid, ids, *args):
#         for obj in self.browse(cr,uid,ids):
#             self.write(cr, uid, ids, {'state':'done'})
#         return True
    
    
    @api.multi
    def button_confirm(self):
        for obj in self:
            if obj.adult + obj.child == 0:
                raise UserError(' Please Enter number of  Adults and Child ')
            if not obj.customer_line_ids:
                raise UserError(' Please Enter Customer Details')
            adult_len = 0
            child_len = 0
            for customer in obj.customer_line_ids:
                if customer.type == 'adult':
                    adult_len += 1
                else:
                    child_len += 1
            print(adult_len,"adult_len",child_len,"child_len")
            if not (adult_len == obj.adult and child_len == obj.child):
                raise UserError('Customer Details is not proper')
            if not obj.checkin_date:
                raise UserError('Please provide Journey Date before confirmation.')
            if obj.tour_id and obj.checkin_date and obj.start_date:
                tot_days = int(obj.tour_id.days)
                
                st_dt = str(obj.start_date.start_date).split(' ')[0],
                dt_from = datetime.strptime(st_dt[0], '%Y-%m-%d').date()
                single_date = str(dt_from + timedelta(days=tot_days))
                single_date =datetime.strptime(single_date,'%Y-%m-%d').date()
                if (obj.checkin_date < obj.start_date.start_date or obj.checkin_date > single_date):
                    raise UserError('You are giving wrong Journey Date.')
            if not (obj.cost_price and obj.sale_price and obj.cost_price_child and obj.sale_price_child):
                raise Warning("Rate is not define for above transport information.")
        return self.write({'state':'confirm'})
    
#     def button_confirm(self, cr, uid, ids, context=None):
#         for obj in self.browse(cr,uid,ids):
#             if obj.adult + obj.child == 0:
#                 raise osv.except_osv(_('Error !'), _(' Please Enter number of  Adults and Child '))
#             if not obj.customer_line_ids:
#                 raise osv.except_osv(_('Error !'), _(' Please Enter Customer Details'))
#             adult_len = 0
#             child_len = 0
#             for customer in obj.customer_line_ids:
#                 if customer.type == 'adult':
#                     adult_len += 1
#                 else:
#                     child_len += 1
#             print(adult_len,"adult_len",child_len,"child_len")
#             if not (adult_len == obj.adult and child_len == obj.child):
#                 raise osv.except_osv(_('Error !'), _('Customer Details is not proper'))
#             if not obj.checkin_date:
#                 raise osv.except_osv(_('Error !'), _('Please provide Journey Date before confirmation.'))
#             if obj.tour_id and obj.checkin_date and obj.start_date:
#                 tot_days = int(obj.tour_id.days)
#                 st_dt = obj.start_date.start_date.split(' ')[0],
#                 dt_from = mx.DateTime.strptime(st_dt[0], '%Y-%m-%d')
#                 single_date = str(dt_from + RelativeDateTime(days=tot_days))
#                 print("single_date",single_date[0:10])
#                 if (obj.checkin_date < obj.start_date.start_date or obj.checkin_date > single_date[0:10]):
#                     raise osv.except_osv(_('Error !'), _('You are giving wrong Journey Date.'))
#             if not (obj.cost_price and obj.sale_price and obj.cost_price_child and obj.sale_price_child):
#                 raise osv.except_osv(_("Warning"),_("Rate is not define for above transport information."))
#         return self.write(cr, uid, ids, {'state':'confirm'})
    

