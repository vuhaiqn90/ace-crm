import time
from odoo import fields, models, api
from odoo.tools.translate import _
from datetime import datetime, timedelta
from odoo.exceptions import UserError,Warning

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

    self._cr.execute(
                'SELECT i.* '
                'FROM product_pricelist_item AS i '
                'WHERE id = '+str(plversion_ids[0].id)+'')
                
    res1 = self._cr.dictfetchall()
    if pricelist_obj:
        price=currency_obj.compute( price, pricelist_obj.currency_id.id, round=False)
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







class tour_hotel_reservation(models.Model):
    _name = "tour.hotel.reservation"
    _description = "Tour Hotel Reservation"
    
    
    
    def get_partner_lang_date(self,date1,lang):       
        record = self.env['res.lang'].search([('code','=',lang)])
        if date1 == False:
            new_date=" "        
        
        else:
            new_date=datetime.strptime(str(date1),'%Y-%m-%d').date()
        return new_date
    
#     def get_partner_lang_date(self, cr, uid, ids, date1,lang):       
#         search_id = self.pool.get('res.lang').search(cr,uid,[('code','=',lang)])
#         record=self.pool.get('res.lang').browse(cr,uid,search_id)
#         new_date=datetime.strftime(datetime.strptime(date1,'%Y-%m-%d'),record.date_format)
#         print("!!!!!!!!!!!!!!!!---new date=",new_date)        
#         return new_date
    
    
    @api.model
    def create(self, vals): 
        # function overwrites create method and auto generate request no. 
        req_no = self.env['ir.sequence'].get('tour.hotel.reservation')
        vals['name'] = req_no
        return super(tour_hotel_reservation, self).create(vals)
    
#     def create(self, cr, uid, vals, context=None): 
#         # function overwrites create method and auto generate request no. 
#         req_no = self.pool.get('ir.sequence').get(cr,uid,'tour.hotel.reservation'),
#         vals['name'] = req_no[0]
#         return super(tour_hotel_reservation, self).create(cr, uid, vals, context=context)
    
    
    @api.depends('checkin_date','checkout_date')
    def _get_no_of_days(self):
        res = {}
        diff_day = 0
        
        for obj in self:
            if obj.checkin_date and obj.checkout_date:
                from_dt = time.mktime(time.strptime(str(obj.checkin_date),'%Y-%m-%d'))
                to_dt = time.mktime(time.strptime(str(obj.checkout_date),'%Y-%m-%d'))
                diff_day = (to_dt-from_dt)/(3600*24)
                res[obj.id] = round(diff_day)
                self.no_of_days = round(diff_day)
        #return res
    
#     def _get_no_of_days(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         diff_day = 0
#         for obj in self.browse(cr, uid, ids):
#             if obj.checkin_date and obj.checkout_date:
#                 from_dt = time.mktime(time.strptime(obj.checkin_date,'%Y-%m-%d'))
#                 to_dt = time.mktime(time.strptime(obj.checkout_date,'%Y-%m-%d'))
#                 diff_day = (to_dt-from_dt)/(3600*24)
#                 res[obj.id] = round(diff_day)
#         return res 
    
    
    
    def _get_total_amt(self):
        res = {}
        total = 0
        for obj in self:
            if obj.checkin_date and obj.checkout_date:
                no_of_day = obj._get_no_of_days()
                for no_qty in no_of_day.values():
                    untax_amt= obj.hotel_rent * no_qty * obj.room_required
                    tax_amt = obj._get_tax_amt()
                    for tx_amt in tax_amt.values():
                        total =  tx_amt + untax_amt
            res[obj.id] = total
        return res
    
#     def _get_total_amt(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         total = 0
#         
#         for obj in self.browse(cr, uid, ids):
#             if obj.checkin_date and obj.checkout_date:
#                 no_of_day = self._get_no_of_days(cr,uid,obj.id,'args1','args2',context)
#                 for no_qty in no_of_day.values():
#                     untax_amt= obj.hotel_rent * no_qty * obj.room_required
#                     tax_amt = self._get_tax_amt(cr,uid,ids,args1,args2,context)
#                     for tx_amt in tax_amt.values():
#                         total =  tx_amt + untax_amt
#             res[obj.id] = total
#         return res
#     
#     

    def _amount_customer_line_tax(self):
        val = 0.0
        if self.checkin_date and self.checkout_date:
            no_of_day = self._get_no_of_days()
            for no_qty in no_of_day.values():
                tax = self.tax_ids.compute_all(self.hotel_rent, None, no_qty, self.room_type_id)
                for c in tax['taxes']:
                    val += c.get('amount', 0.0)
        return val

#     def _amount_customer_line_tax(self, cr, uid, line, context=None):
#         val = 0.0
#         if line.checkin_date and line.checkout_date:
#             no_of_day = self._get_no_of_days(cr,uid,line.id,'args1','args2',context)
#             for no_qty in no_of_day.values():
#                 tax = line.tax_ids.compute_all(line.hotel_rent, None, no_qty, line.room_type_id)
#                 for c in tax['taxes']:
#                     val += c.get('amount', 0.0)
#         return val
    
    
    
    def _amount_supplier_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        if line.checkin_date and line.checkout_date:
            no_of_day = line._get_no_of_days()
            for no_qty in no_of_day.values():
                tax = line.tax_ids.compute_all(line.room_rent, None, no_qty, line.room_type_id)
                for c in tax['taxes']:
                    val += c.get('amount', 0.0)
        return val
    
#     def _amount_supplier_line_tax(self, cr, uid, line, context=None):
#         val = 0.0
#         if line.checkin_date and line.checkout_date:
#             no_of_day = self._get_no_of_days(cr,uid,line.id,'args1','args2',context)
#             for no_qty in no_of_day.values():
#                 tax = line.tax_ids.compute_all(line.room_rent, None, no_qty, line.room_type_id)
#                 for c in tax['taxes']:
#                     val += c.get('amount', 0.0)
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
    
    
    
    def _get_hotel_invoice_amt(self):
        res = {}
        total = 0
        invoice_amt = 0
        val=0.0
        for obj in self:
            if obj.checkin_date and obj.checkout_date:
                val = obj._amount_supplier_line_tax() #calculation tax amount for suppliter
                no_of_day = obj._get_no_of_days()
                for no_qty in no_of_day.values():
                    invoice_amt = obj.room_rent * no_qty * obj.room_required
                    total =  val + invoice_amt
            print("total",total)
            res[obj.id] = total
        return res
    
#     def _get_hotel_invoice_amt(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         total = 0
#         invoice_amt = 0
#         val=0.0
#         for obj in self.browse(cr, uid, ids):
#             if obj.checkin_date and obj.checkout_date:
#                 val = self._amount_supplier_line_tax(cr, uid, obj, context=context) #calculation tax amount for suppliter
#                 no_of_day = self._get_no_of_days(cr, uid, obj.id, 'args1', 'args2', context)
#                 for no_qty in no_of_day.values():
#                     invoice_amt = obj.room_rent * no_qty * obj.room_required
#                     total =  val + invoice_amt
#             print("total",total)
#             res[obj.id] = total
#         return res
    
    
    def _get_untax_amt(self):
        res = {}
        total = 0
        for obj in self:
            if obj.checkin_date and obj.checkout_date:
                no_of_day = obj._get_no_of_days()
                for no_qty in no_of_day.values():
                    total =  obj.hotel_rent * no_qty * obj.room_required
                res[obj.id] = total
        return res
    
#     def _get_untax_amt(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         total = 0
#         for obj in self.browse(cr,uid,ids):
#             if obj.checkin_date and obj.checkout_date:
#                 no_of_day = self._get_no_of_days(cr, uid, obj.id, 'args1', 'args2', context)
#                 for no_qty in no_of_day.values():
#                     total =  obj.hotel_rent * no_qty * obj.room_required
#                 res[obj.id] = total
#         return res 
    
  
    
    name = fields.Char("Registration ID",size=50,readonly=True)
    current_date = fields.Date("Date",required=True,readonly=True, states={'draft': [('readonly', False)]})
    checkin_date = fields.Date("Check In Date",readonly=True, states={'draft': [('readonly', False)]})
    checkout_date = fields.Date("Check Out Date",readonly=True, states={'draft': [('readonly', False)]})
    customer_id = fields.Many2one('res.partner','Customer',required=True,readonly=True, states={'draft': [('readonly', False)]})
#                'address_id':fields.many2one('res.partner.address','Customer Address',required=True,readonly=True, states={'draft': [('readonly', False)]}),
    email_id = fields.Char('Email Id',size=150,readonly=True, states={'draft': [('readonly', False)]})
    mobile = fields.Char('Mobile Number',size=164,required=True,readonly=True, states={'draft': [('readonly', False)]})
    adult = fields.Integer("Adult Persons",readonly=True, states={'draft': [('readonly', False)]})
    child = fields.Integer("Child",readonly=True, states={'draft': [('readonly', False)]})
    room_type_id = fields.Many2one('product.product',"Room Type",readonly=True, states={'draft': [('readonly', False)]})
    room_rent = fields.Float('Cost Price',help = "Generates Supplier invoice of this amount",readonly=True, states={'draft': [('readonly', False)]})
    hotel_rent = fields.Float('Sale Price',help="Generates Customer invoice of this amount",readonly=True, states={'draft': [('readonly', False)]})
    room_required = fields.Integer("Rooms Required",readonly=True, states={'draft': [('readonly', False)]})
    no_of_days = fields.Float(compute=_get_no_of_days, string="No. Of Days", store=True)
    hotel_type_id = fields.Many2one('hotel.type','Hotel Type',required=True,readonly=True, states={'draft': [('readonly', False)]})
    hotel_id = fields.Many2one('hotel.information',"Hotel",required=True)
    tour_customer_ids = fields.One2many('tour.customer.details','hotel_res_id','Tour Customer Details',states={'done': [('readonly', True)]})
    tax_ids = fields.Many2many('account.tax', 'hotel_reservation_tax', 'hotel_res_id', 'tax_id', 'Taxes', readonly=True, states={'draft':[('readonly',False)]})
    hotel_room_reserve_invoice_ids = fields.Many2many('account.invoice','hotel_room_reserve_invoice_rel', 'hotel_book_id', 'invoice_id', 'Hotel Room Reservation Invoices',readonly=True)
    hotel_room_reserve_supplier_invoice_ids = fields.Many2many('account.invoice','hotel_room_reserve_supplier_invoice_rel', 'hotel_book_id', 'invoice_id', 'Hotel Room Reservation Invoices',readonly=True)
    tour_id = fields.Many2one("tour.package","Tour",readonly=True,)
    tour_start_date = fields.Many2one('tour.dates',"Tour Start Date",readonly=True,)
    tour_book_id = fields.Many2one("tour.booking","Tour Booking Ref",readonly=True,)
    destination_id = fields.Many2one('tour.destinations','Tour Destination',readonly=True,)
    untax_amt = fields.Float(compute=_get_untax_amt, string="Untaxed Amt", store=True)
    tax_amt = fields.Float(compute=_get_tax_amt,string="Taxes ", store=True)
    total_amt = fields.Float(compute=_get_total_amt,string="Customer Invoice Amt", store=True,help="This fields shows Amount as per the currency of selected pricelist at header.")
    hotel_invoice_amt = fields.Float(compute=_get_hotel_invoice_amt,string="Hotel Invoice Amt", store=True,help="This fields shows Amount as per the currency of selected pricelist at header.However, supplier invoice shall be raise based on the currency of pricelist linked with supplier.")
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist',required=True,readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
                               ('draft', 'Draft'),
                               ('confirm', 'Confirm'),
                               ('request', "Waiting For Hotel Approval"),
                               ('approve', 'Approved'),
                               ('book', "Booked"),
                               ('issue', "Ticket Issue"),
                               ('done', "Done"),
                               ('cancel', 'Canceled'),
                               ], 'Status',readonly=True,default=lambda * a: 'draft')
                    

#    def on_change_customer_id(self,cr,uid,ids,customer_id):
#        result = {}
#        invoice_addr_id = False
#        if customer_id:
#            res = self.pool.get('res.partner').address_get(cr, uid, [customer_id], ['delivery', 'invoice', 'contact'])
#            if res['invoice']:
#                invoice_addr_id = res['invoice']
#                obj = self.pool.get('res.partner.address').browse(cr,uid,invoice_addr_id)
#                result['email_id'] = obj.email
#                result['mobile'] = obj.mobile
#            else:
#                res_add = self.pool.get('res.partner.address').search(cr, uid, [('partner_id', '=', customer_id)])
#                if res_add:
#                    invoice_addr_id = res_add
#                    obj = self.pool.get('res.partner.address').browse(cr,uid,invoice_addr_id)
#                    result['email_id'] = obj.email
#                    result['mobile'] = obj.mobile
#            result['address_id'] = invoice_addr_id
#        return {'value': result}
    
    
    def button_cancel(self):
        self.write({'state':'cancel'})
        return True
    
#     def button_cancel(self, cr, uid, ids, *args):
#         self.write(cr, uid, ids, {'state':'cancel'})
#         return True
    
    @api.onchange('room_type_id')
    def onchange_room_type(self):
        if self.room_type_id and not self.hotel_id:
            raise Warning("Please select Hotel first")
        
        for room_type in self.hotel_id.room_info_ids:
           if room_type.name==self.room_type_id.name:
               self.room_rent=room_type.cost_price
               self.hotel_rent=room_type.sale_price
            #room_ids = self.env['product.product'].search([('name','=',room_type.name)])
            #print (hotel_type_ids.room_info_ids)
            #for cost_price1 in hotel_type_ids.room_info_ids:
            #       print (cost_price1.cost_price)
            #print (room_ids)
            #for product in room_ids:
            #    product_ids.append(product.id)
            #print (product_ids)
        
        result = {}
        warning = {}
        if self.room_type_id:
            tax_list = []
            for tax in self.room_type_id.taxes_id:
                tax_list.append(tax.id)
            result['tax_ids'] = [(6,0,tax_list)]
            ##indrajeet committedd according to odoo 9 changes .....
            ## commited becouse pricelist_ids removed from product.supplierinfo object 
            ##so we can not access pricelist_id , price , saleprice......
            
            if self.room_type_id.seller_ids:
                for line in self.room_type_id.seller_ids:
                    if line.name.id == self.hotel_id:
                        result['room_rent'] = get_price(self.pricelist_id.id, line.price)
                        result['hotel_rent'] = get_price(self.pricelist_id.id, line.sale_price)
                    
            else:
                warn_msg = _("Rate is not define for above Hotel information.")
                warning = {
                    'title': _('Warning !'),
                    'message': warn_msg
                    }
        return {'value': result,'warning': warning}
    
    @api.onchange('hotel_type_id')
    def onchange_hoteltype(self):
        if self.hotel_type_id and not self.pricelist_id:
            raise Warning("Please select Pricelist first")
        
        
        
        
    @api.onchange('hotel_id')
    def onchange_hotelid(self):
        if self.hotel_id and not self.hotel_type_id:
            raise Warning("Please select Hotel Type first")
        
        elif self.hotel_id :
            product_ids=[]
            hotel_type_ids = self.env['hotel.information'].search([('hotel_id','=',self.hotel_id.name)],limit=1)
            print (hotel_type_ids)
            #tour_ids_with_same_season = []
        
            for room_type in hotel_type_ids.room_info_ids:
                room_ids = self.env['product.product'].search([('name','=',room_type.name)])
                print (hotel_type_ids.room_info_ids)
                #for cost_price1 in hotel_type_ids.room_info_ids:
                #       print (cost_price1.cost_price)
                print (room_ids)
                for product in room_ids:
                    product_ids.append(product.id)
                print (product_ids)
            #room_in_same_hotel.append(room_type.id)
            #print (room_in_same_hotel)
            
            #return roomtyp['AC','NONAC']
#                 [tour_ids_with_same_season.append(line.tour_id.id) for line in tour.tour_date_lines if line.season_id.id==self.season_id.id]
#         #print (tour_ids_with_same_season)
            return {
                'domain':{
                            'room_type_id':[('id','in',product_ids)]
                         }
                   }


    
        
#     def onchange_room_type(self,cr,uid,ids,room_type_id,hotel_id,price_list):
#         result = {}
#         warning = {}
#         if not price_list:
#             raise osv.except_osv(_('Warning !'), _('Pricelist is not selected.'))
#         if not hotel_id:
#             raise osv.except_osv(_('Warning !'), _('Hotel is not selected.'))
#         print("onchange_room_type")
#         if room_type_id:
#             pricelist_id = self.pool.get('product.pricelist').browse(cr,uid,price_list)
#             res = self.pool.get('product.product').browse(cr,uid,room_type_id)
#             tax_list = []
#             for tax in res.taxes_id:
#                 tax_list.append(tax.id)
#             result['tax_ids'] = [(6,0,tax_list)]
#             ##indrajeet committedd according to odoo 9 changes .....
#             ## commited becouse pricelist_ids removed from product.supplierinfo object 
#             ##so we can not access pricelist_id , price , saleprice......
#             
#             if res.seller_ids:
#                 for line in res.seller_ids:
#                     if line.name.id == hotel_id:
#                         result['room_rent'] = get_price(self, cr, uid, ids, pricelist_id.id, line.price)
#                         result['hotel_rent'] = get_price(self, cr, uid, ids, pricelist_id.id, line.sale_price)
#                     
#             else:
#                 warn_msg = _("Rate is not define for above Hotel information.")
#                 warning = {
#                     'title': _('Warning !'),
#                     'message': warn_msg
#                     }
#         return {'value': result,'warning': warning}
    
    
    @api.multi
    def compute_amt(self):
        print("compute_amt")
        for obj in self:
            if not (obj.room_rent and obj.hotel_rent):
                raise Warning('Rate is not define for above Hotel information.')
        return True
    
#     def compute_amt(self, cr, uid, ids, *args):
#         print("compute_amt")
#         for obj in self.browse(cr,uid,ids):
#             if not (obj.room_rent and obj.hotel_rent):
#                 raise osv.except_osv(_('Warning !'), _('Rate is not define for above Hotel information.'))
#         return True
    
#     _defaults = {
#                  'state': lambda * a: 'draft',
#                  }

    
    @api.multi
    def make_confirm(self):
        for obj in self:
            if not (obj.room_rent and obj.hotel_rent):
                raise Warning('Rate is not define for above Hotel information.')
            if not obj.checkin_date:
                raise UserError(' Please ADD Check-In Date Before Confirm')
            if not obj.checkout_date:
                raise UserError(' Please ADD Check-Out Date Before Confirm')
            if obj.room_required == 0:
                raise UserError(' Please Enter How Many Rooms Required')
            if obj.adult + obj.child == 0:
                raise UserError(' Please Enter Details of Person like Adults And Child ')
            if obj.checkin_date > obj.checkout_date:
                raise UserError(' Please Check The Check out Date Which Is Less Than Check In Date')  
            if not obj.tour_customer_ids:
                raise UserError('Please enter customer details')
            if obj.tour_id:
                tot_days = int(obj.tour_id.days)
                st_dt = str(obj.tour_start_date.start_date).split(' ')[0],
                dt_from = datetime.strptime(st_dt[0], '%Y-%m-%d').date()
                single_date = str(dt_from + timedelta(days=tot_days))
                single_date=datetime.strptime(single_date,'%Y-%m-%d').date()
                
                if (obj.checkin_date < obj.tour_start_date.start_date or obj.checkin_date > single_date):
                    raise UserError('You are giving wrong check in date')
                if (obj.checkout_date < obj.tour_start_date.start_date or obj.checkout_date > single_date):
                    raise UserError('You are giving wrong checkout date')

        self.write({'state':'confirm'})
        return True
#     def make_confirm(self, cr, uid, ids, *args):
#         for obj in self.browse(cr,uid,ids):
#             if not (obj.room_rent and obj.hotel_rent):
#                 raise osv.except_osv(_('Warning !'), _('Rate is not define for above Hotel information.'))
#             if not obj.checkin_date:
#                 raise osv.except_osv(_('Error !'), _(' Please ADD Check-In Date Before Confirm'))
#             if not obj.checkout_date:
#                 raise osv.except_osv(_('Error !'), _(' Please ADD Check-Out Date Before Confirm'))
#             if obj.room_required == 0:
#                 raise osv.except_osv(_('Error !'), _(' Please Enter How Many Rooms Required'))
#             if obj.adult + obj.child == 0:
#                 raise osv.except_osv(_('Error !'), _(' Please Enter Details of Person like Adults And Child '))
#             if obj.checkin_date > obj.checkout_date:
#                 raise osv.except_osv(_('Error !'), _(' Please Check The Check out Date Which Is Less Than Check In Date'))  
#             if not obj.tour_customer_ids:
#                 raise osv.except_osv(_('Error !'), _('Please enter customer details'))
#             if obj.tour_id:
#                 tot_days = int(obj.tour_id.days)
#                 st_dt = obj.tour_start_date.start_date.split(' ')[0],
#                 dt_from = datetime.strptime(st_dt[0], '%Y-%m-%d')
#                 single_date = str(dt_from + timedelta(days=tot_days))
#                 print("single_date",single_date[0:10])
#                 if (obj.checkin_date < obj.tour_start_date.start_date or obj.checkin_date > single_date[0:10]):
#                     raise osv.except_osv(_('Error !'), _('You are giving wrong check in date')) 
#                 if (obj.checkout_date < obj.tour_start_date.start_date or obj.checkout_date > single_date[0:10]): 
#                     raise osv.except_osv(_('Error !'), _('You are giving wrong checkout date')) 
#         self.write(cr, uid, ids, {'state':'confirm'})
#         return True
    
    
    def send_to_hotel(self):
        self.write({'state':'request'})
        return True
    
#     def send_to_hotel(self, cr, uid, ids, *args):
#         self.write(cr, uid, ids, {'state':'request'})
#         return True
    
    
    def make_approval(self):
        self.write({'state':'approve'})
        return True
    
#     def make_approval(self, cr, uid, ids, *args):
#         self.write(cr, uid, ids, {'state':'approve'})
#         return True

    @api.multi
    def make_booking(self):
        ctx = dict(self._context or {})

        for obj in self:
            rooms = obj.room_required
            room_number = []
            for line in obj.tour_customer_ids:
                if ctx.get('continue_booking'):
                    # TODO: continue_booking
                    if not line.room_no:
                        self.tour_customer_ids.room_no=self.room_type_id.name
                elif ctx.get('cancel_booking'):
                    # TODO: cancel_booking
                    return True
                else:
                    return {
                        'name': _('Room Number Set'),
                        'type': 'ir.actions.act_window',
                        'res_model': 'confirm.room',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'target': 'new'
                    }

                if not line.room_no:
                    raise Warning("Room Number is not Allocated to Customer")
                room_number.append(line.room_no)
            a = set(room_number)
            if rooms != len(a):
                raise Warning("Number of Rooms Required is not equal to Total Rooms Allocated To Customers")

            if not obj.tour_id:
                acc_id = obj.customer_id.property_account_receivable_id.id
                journal_obj = self.env['account.journal']
                journal_ids = journal_obj.search([('type', '=', 'sale')], limit=1)
                type = 'out_invoice'
                inv = {
                    'name': obj.name,
                    'origin': obj.name,
                    'type': type,
                    'reference': "Hotel Room Reservation",
                    'account_id': acc_id,
                    'partner_id': obj.customer_id.id,
                    'currency_id': obj.pricelist_id.currency_id.id,
                    'journal_id': len(journal_ids) and journal_ids[0].id or False,
                    'amount_tax': obj.tax_amt,
                    'amount_untaxed': obj.untax_amt,
                    'amount_total': obj.total_amt,
                }
                inv_id = self.env['account.invoice'].create(inv)
                tax = []
                for i in obj.tax_ids:
                    tax.append(i.id)
                account_id = obj.room_type_id.property_account_income_id.id
                if not account_id:
                    account_id = obj.room_type_id.categ_id.property_account_income_categ_id.id
                if not account_id:
                    raise UserError('There is no income account defined ' \
                                    'for this product: "%s" (id:%d)' % \
                                    obj.room_type_id.name, obj.room_type_id.id)
                il = {
                    'name': obj.name,
                    'product_id': obj.room_type_id.id,
                    'account_id': account_id,
                    'price_unit': obj.untax_amt,
                    'quantity': 1.0,
                    'uos_id': False,
                    'origin': obj.name,
                    'invoice_id': inv_id.id,
                    'pay_date': obj.current_date,
                    'order_amt': obj.untax_amt,
                    'invoice_line_tax_id': [(6, 0, tax)],
                }

                self.env['account.invoice.line'].create(il)
                self._cr.execute('insert into hotel_room_reserve_invoice_rel(hotel_book_id,invoice_id) values (%s,%s)',
                                 (obj.id, inv_id.id))

        #             acc_id = obj.hotel_id.property_account_payable_id.id
#             journal_obj = self.env['account.journal']
#             journal_ids = journal_obj.search([('type', '=','purchase')], limit=1)
#             line_account_id = obj.room_type_id.product_tmpl_id.property_account_expense_id.id
#             if not line_account_id:
#                 line_account_id = obj.room_type_id.categ_id.property_account_expense_categ_id.id
#             if not line_account_id:
#                 raise UserError('There is no income account defined ' \
#                                 'for this product: "%s" (id:%d)' % \
#                                 obj.room_type_id.name, obj.room_type_id.id,)
#             
#             tax_amount = get_price(self,obj.hotel_id.property_product_pricelist.id, obj.tax_amt)
#             untax_amount = get_price(self,obj.hotel_id.property_product_pricelist.id, obj.untax_amt)
#             total_hotel_amount = get_price(self,obj.hotel_id.property_product_pricelist.id, obj.hotel_invoice_amt)
#             
#             type = 'in_invoice' 
#             inv = {
#                         'name': obj.name,
#                         'origin': obj.name,
#                         'type': type,
#                         'reference': "Hotel Room Reservation Invoice",
#                         'account_id': acc_id,
#                         'partner_id': obj.hotel_id.id,
#                         'currency_id': obj.hotel_id.property_product_pricelist.id,
#                         'journal_id': len(journal_ids) and journal_ids[0].id or False,
#                         'amount_tax':tax_amount,
#                         'amount_untaxed':untax_amount,
#                         'amount_total':total_hotel_amount,
#                         }
#             inv_id = self.env['account.invoice'].create(inv)
#             tax = []
#             for i in obj.tax_ids:
#                 tax.append(i.id)
#             il = {
#                     'name': obj.name,
#                     'product_id':obj.room_type_id.id,
#                     'account_id': line_account_id,
#                     'price_unit':total_hotel_amount, 
#                     'quantity': 1.0,
#                     'uos_id':  False,
#                     'origin':obj.name,
#                     'invoice_id':inv_id.id,
#                     'pay_date':obj.current_date,
#                     'order_amt':total_hotel_amount,
#                     'invoice_line_tax_id':[(6,0,tax)],
#                 }
#             self.env['account.invoice.line'].create(il)
#             self._cr.execute('insert into hotel_room_reserve_supplier_invoice_rel(hotel_book_id,invoice_id) values (%s,%s)', (obj.id, inv_id.id))
#     
        self.write({'state':'book'})
        return True
    
#     def make_booking(self, cr, uid, ids, *args):
#         for obj in self.browse(cr,uid,ids):
#             rooms = obj.room_required
#             room_number = []
#             for line in obj.tour_customer_ids:
#                 if not line.room_no:
#                     raise osv.except_osv(_("Warning"),_("Room Number is not Allocated to Customer"))
#                 room_number.append(line.room_no)
#             a = set(room_number)
#             if rooms != len(a):
#                 raise osv.except_osv(_("Warning"),_("Number of Rooms Required is not equal to Total Rooms Allocated To Customers"))
#                         
#             if not obj.tour_id:
#                 acc_id = obj.customer_id.property_account_receivable_id.id
#                 journal_obj = self.pool.get('account.journal')
#                 journal_ids = journal_obj.search(cr, uid, [('type', '=','sale')], limit=1)
#                 type = 'out_invoice' 
#                 inv = {
#                             'name': obj.name,
#                             'origin': obj.name,
#                             'type': type,
#                             'reference': "Hotel Room Reservation",
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
#                 print("tax_id",obj.tax_ids)
#                 tax = []
#                 for i in obj.tax_ids:
#                     tax.append(i.id)
#                 account_id = obj.room_type_id.property_account_income_id.id
#                 if not account_id:
#                     account_id = obj.room_type_id.categ_id.property_account_income_categ_id.id
#                 if not account_id:
#                     raise osv.except_osv(_('Error !'),
#                             _('There is no income account defined ' \
#                                     'for this product: "%s" (id:%d)') % \
#                                     (obj.room_type_id.name, obj.room_type_id.id,))
#                 il = {
#                         'name': obj.name,
#                         'product_id':obj.room_type_id.id,
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
#                 cr.execute('insert into hotel_room_reserve_invoice_rel(hotel_book_id,invoice_id) values (%s,%s)', (obj.id, inv_id))
#                 
#                 
#                 
#             acc_id = obj.hotel_id.property_account_payable_id.id
#             journal_obj = self.pool.get('account.journal')
#             journal_ids = journal_obj.search(cr, uid, [('type', '=','purchase')], limit=1)
#             line_account_id = obj.room_type_id.product_tmpl_id.property_account_expense_id.id
#             if not line_account_id:
#                 line_account_id = obj.room_type_id.categ_id.property_account_expense_categ_id.id
#             if not line_account_id:
#                 raise osv.except_osv(_('Error !'),
#                         _('There is no income account defined ' \
#                                 'for this product: "%s" (id:%d)') % \
#                                 (obj.room_type_id.name, obj.room_type_id.id,))
#             
#             tax_amount = get_price(self, cr, uid, ids, obj.hotel_id.property_product_pricelist.id, obj.tax_amt)
#             untax_amount = get_price(self, cr, uid, ids, obj.hotel_id.property_product_pricelist.id, obj.untax_amt)
#             total_hotel_amount = get_price(self, cr, uid, ids, obj.hotel_id.property_product_pricelist.id, obj.hotel_invoice_amt)
#             
#             type = 'in_invoice' 
#             inv = {
#                         'name': obj.name,
#                         'origin': obj.name,
#                         'type': type,
#                         'reference': "Hotel Room Reservation Invoice",
#                         'account_id': acc_id,
#                         'partner_id': obj.hotel_id.id,
#                         'currency_id': obj.hotel_id.property_product_pricelist.id,
#                         'journal_id': len(journal_ids) and journal_ids[0] or False,
#                         'amount_tax':tax_amount,
#                         'amount_untaxed':untax_amount,
#                         'amount_total':total_hotel_amount,
#                         }
#             print("inv",inv)
#             inv_id = self.pool.get('account.invoice').create(cr, uid, inv)
#             print("tax_id",obj.tax_ids)
#             tax = []
#             for i in obj.tax_ids:
#                 tax.append(i.id)
#             il = {
#                     'name': obj.name,
#                     'product_id':obj.room_type_id.id,
#                     'account_id': line_account_id,
#                     'price_unit':total_hotel_amount, 
#                     'quantity': 1.0,
#                     'uos_id':  False,
#                     'origin':obj.name,
#                     'invoice_id':inv_id,
#                     'pay_date':obj.current_date,
#                     'order_amt':total_hotel_amount,
#                     'invoice_line_tax_id':[(6,0,tax)],
#                     }
#             print("il",il)
#             self.pool.get('account.invoice.line').create(cr, uid, il,)
#             cr.execute('insert into hotel_room_reserve_supplier_invoice_rel(hotel_book_id,invoice_id) values (%s,%s)', (obj.id, inv_id))
#     
#         self.write(cr, uid, ids, {'state':'book'})
#         return True

       
    @api.multi
    def issue_ticket(self):
        for obj in self:
            if not obj.tour_id:
                if obj.hotel_room_reserve_invoice_ids[0].state !='paid':
                    raise Warning("Please Pay The Invoice Amount ")
            self.write({'state':'issue'})
        return True
    
#     def issue_ticket(self, cr, uid, ids, *args):
#         for obj in self.browse(cr,uid,ids):
#             if not obj.tour_id:
#                 if obj.hotel_room_reserve_invoice_ids[0].state !='paid':
#                     raise osv.except_osv(_("Warning"),_("Please Pay The Invoice Amount "))
#             self.write(cr, uid, ids, {'state':'issue'})
#         return True
    
    
    def make_done(self):
        self.write({'state':'done'})
        return True
    
#     def make_done(self, cr, uid, ids, *args):
#         self.write(cr, uid, ids, {'state':'done'})
#         return True
    
    
        
class tour_customer_details(models.Model):
    _inherit = "tour.customer.details"
    _description = "Tour Customer Details Inheritance"

    hotel_res_id = fields.Many2one('tour.hotel.reservation','Tour Hotel Booking Ref')
    room_no = fields.Char('Room Number',size=64)
    

class product_supplierinfo(models.Model):
    _inherit = "product.supplierinfo"
    _description = "Hotel supplier Info Inheritance"
 
    sale_price = fields.Float('Sale Price')

