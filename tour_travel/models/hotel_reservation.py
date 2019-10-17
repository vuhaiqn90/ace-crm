import time
from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError,Warning


# class hotel_book(osv.osv):
#     _name = "hotel.book"



class hotel_type(models.Model):
    _name = "hotel.type"
    _description = "Hotel Type Configuration"
    
    name = fields.Char("Hotel Type",size=50,required=True)
    description = fields.Char("Description",size=60)


class room_type(models.Model):
    _name = "room.type"
    _description = "Room Type Configuration"
    
    name = fields.Char("Description",size=50,required=True)
    room_type = fields.Many2one("product.product","Room Type",required=True)
    
    
    @api.onchange('room_type')
    def on_change_room_type(self):
        result = {}
        if self.room_type:
            result['name'] = self.room_type.name
            search_id = self.env['product.category'].search([('name','=', 'Room Types')], limit=1)
            if search_id:
                self.room_type.write({'categ_id':search_id.id})

        return {'value': result}





# class Product_form(models.Model):
#     _inherit = 'product.template'
#
#
#     # @api.model
#     # def default_get(self, fields):
#     #     res = super(Product_form,self).default_get(fields)
#     #     print('Fields1111111111111111111111111111111111111111111111 : ',fields)
#     #     print('Fields1111111111111111111111111111111111111111111111 : ',res)
#     #     search_id = self.env['product.category'].search([('name', '=', 'Room Types')], limit=1)
#     #     if search_id:
#     #           res['categ_id']=search_id.id
#     #
#     #     return res
#
#     categ_id = fields.Many2one('product.category',string="cate")
#
#     @api.multi
#     def action_confirm(self):
#         res = super(Product_form, self).action_confirm()
#         self.categ_id = "hello"
#         return res


    
#     def on_change_room_type(self,cr,uid,ids,room_type):
#         result = {}
#         if room_type:
#             obj = self.pool.get('product.product').browse(cr,uid,room_type)
#             result['name'] = obj.name
#         return {'value': result}




class service_type(models.Model):
    _name = "service.type"
    _description = "Hotel Service Type Configuration"
    
    name = fields.Char("Description",size=50,required=True)
    service_id = fields.Many2one("product.product","Service",required=True)
    
    
    @api.onchange('service_id')
    def on_change_service_id(self):
        result = {}
        result['name'] = self.service_id.name
        return {'value': result}
    
#     def on_change_service_id(self,cr,uid,ids,service_id):
#         result = {}
#         prod_obj = self.pool.get('product.template').browse(cr,uid,service_id)
#         result['name'] = prod_obj.name
#         return {'value': result}  
    


class hotel_information(models.Model):
    _name = "hotel.information"
    _description = "Hotel Information "
    
    
    name = fields.Char("Name",size=50,required=True)
    hotel_id = fields.Many2one('res.partner',"Hotel",required=True)
    room_info_ids = fields.One2many('room.info',"hotel_id","Room Information")
    service_info_ids = fields.One2many('hotel.service',"hotel_id1","Service Information")
    hotel_type_id = fields.Many2one('hotel.type','Hotel Type',required=True)
    hotel_type_id_disp = fields.Many2one('hotel.type','Hotel Type',related="hotel_type_id")
    hotel_img1 = fields.Binary('Hotel Image1')
    hotel_img2 = fields.Binary('Hotel Image2')
    hotel_img3 = fields.Binary('Hotel Image3')
    
#     hotel_recv_acc = fields.property(
#                             type='many2one',
#                             relation='account.account',
#                             string="Receivable Account",
#                             method=True,
#                             required=False
#                                     )
    hotel_recv_acc = fields.Many2one(
                            'account.account',
                            string="Receivable Account",
                            required=False)
    
#     hotel_payble_acc = fields.property(
#                             type='many2one',
#                             relation='account.account',
#                             string="Payable Account",
#                             method=True,
#                             required=False)
    
    hotel_payble_acc = fields.Many2one(
                            'account.account',
                            string="Payable Account",
                            required=False)
    
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('done', 'Not Available')], 'Status',readonly=True,default=lambda *a: "draft")
    
#     _defaults = {
#                  "state": lambda *a: "draft",
#                  }
    
    
    @api.onchange('hotel_id')
    def on_change_hotel_id(self):
        result = {}
        invoice_addr_id = False
        if self.hotel_id:
            result['name'] = self.hotel_id.name
            print("result['name']---------------------",result['name'])
            result['hotel_type_id'] = self.hotel_id.hotel_type_id.id
        return {'value': result}
    
#     def on_change_hotel_id(self,cr,uid,ids,hotel_id):
#         result = {}
#         invoice_addr_id = False
#         if hotel_id:
#             partner_id = self.pool.get('res.partner').browse(cr,uid,hotel_id)
#             result['name'] = partner_id.name
#             result['hotel_type_id'] = partner_id.hotel_type_id.id
#         return {'value': result}


    @api.onchange('hotel_id',)
    def on_chnage_hotel(self):
        if self.hotel_id and not self.hotel_id.property_account_receivable_id:
            raise Warning(' Please define customer account')
        self.hotel_recv_acc = self.hotel_id.property_account_receivable_id
        self.hotel_payble_acc = self.hotel_id.property_account_payable_id
    
    @api.multi
    def confirm_info(self):
        for obj in self:
            if not obj.room_info_ids:
                raise UserError(' Please ADD Room Line Before Confirm')
        self.write({'state':'confirm'})
        return True
    
#     def confirm_info(self, cr, uid, ids, *args):
#         for obj in self.browse(cr,uid,ids):
#             if not obj.room_info_ids:
#                 raise osv.except_osv(_('Error !'), _(' Please ADD Room Line Before Confirm'))
#         self.write(cr, uid, ids, {'state':'confirm'})
#         return True

    
#         
    
    

class hotel_reservation(models.Model):
    _name = "hotel.reservation"
    _description = "Hotel Reservation"
    
    
    @api.model
    def create(self,vals): 
        # function overwrites create method and auto generate request no. 
        req_no = self.env['ir.sequence'].get('hotel.reservation'),
        vals['name'] = req_no
        return super(hotel_reservation, self).create(vals)
    
#     def create(self, cr, uid, vals, context=None): 
#         # function overwrites create method and auto generate request no. 
#         req_no = self.pool.get('ir.sequence').get(cr,uid,'hotel.reservation'),
#         vals['name'] = req_no[0]
#         return super(hotel_reservation, self).create(cr, uid, vals, context=context)
    
    
    def _get_total_amt(self):
        res = {}
        total = 0
        for obj in self:
            for i in range (0,len(obj.room_line_ids)):
                total = total + obj.room_line_ids[i].total_price
            for j in range(0,len(obj.service_line_ids)):
                total = total + obj.service_line_ids[j].total_price
            res[obj.id] = total + obj.tax_amt
        return res
    
#     def _get_total_amt(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         total = 0
#         for obj in self.browse(cr, uid, ids):
#             for i in range (0,len(obj.room_line_ids)):
#                 total = total + obj.room_line_ids[i].total_price
#             for j in range(0,len(obj.service_line_ids)):
#                 total = total + obj.service_line_ids[j].total_price
#             res[obj.id] = total + obj.tax_amt
#         return res
    
    
    def _get_tax_amt(self):
        res = {}
        total = 0
        for obj in self:
            print("tax id",obj.tax_id)
            for i in range (0,len(obj.tax_id)):
                total = total + obj.tax_id[i].amount
            res[obj.id] = total
        return res
    
#     def _get_tax_amt(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         total = 0
#         for obj in self.browse(cr, uid, ids):
#             print("tax id",obj.tax_id)
#             for i in range (0,len(obj.tax_id)):
#                 total = total + obj.tax_id[i].amount
#             res[obj.id] = total
#         return res 
    
    
    def _get_untax_amt(self):
        res = {}
        total = 0
        for obj in self:
            for i in range (0,len(obj.room_line_ids)):
                total = total + obj.room_line_ids[i].total_price
            for j in range(0,len(obj.service_line_ids)):
                total = total + obj.service_line_ids[j].total_price
            res[obj.id] = total
        return res
    
#     def _get_untax_amt(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         total = 0
#         for obj in self.browse(cr,uid,ids):
#             for i in range (0,len(obj.room_line_ids)):
#                 total = total + obj.room_line_ids[i].total_price
#             for j in range(0,len(obj.service_line_ids)):
#                 total = total + obj.service_line_ids[j].total_price
#             res[obj.id] = total
#         return res 
    
  
    
    name = fields.Char("Name",size=50)
    current_date = fields.Date("Date",required=True,readonly=True, states={'draft': [('readonly', False)]})
    checkin_date = fields.Date("Check In Date",required=True,readonly=True, states={'draft': [('readonly', False)]})
    checkout_date = fields.Date("Check Out Date",required=True,readonly=True, states={'draft': [('readonly', False)]})
    customer_id = fields.Many2one('res.partner','Customer',required=True,readonly=True, states={'draft': [('readonly', False)]})
    email_id = fields.Char('Email Id',size=150,readonly=True, states={'draft': [('readonly', False)]})
    mobile = fields.Char('Mobile Number',size=164,required=True,readonly=True, states={'draft': [('readonly', False)]})
    adult = fields.Integer("Adult Persons",readonly=True, states={'draft': [('readonly', False)]})
    child = fields.Integer("Child",readonly=True, states={'draft': [('readonly', False)]})
    hotel_type_id = fields.Many2one('hotel.type','Hotel Type',required=True,readonly=True, states={'draft': [('readonly', False)]})
    hotel_id = fields.Many2one('hotel.information',"Hotel",required=True,readonly=True, states={'draft': [('readonly', False)]})
    tax_id = fields.Many2many('account.tax', 'hotel_room_book_tax', 'hotel_id', 'tax_id', 'Taxes', readonly=True, states={'draft':[('readonly',False)]})
    room_line_ids = fields.One2many('room.line',"book_id","Room Line",readonly=True, states={'draft': [('readonly', False)]})
    service_line_ids = fields.One2many('service.line',"book_id","Service Line",readonly=True, states={'draft': [('readonly', False)]})
    room_reserve_invoice_ids = fields.Many2many('account.invoice','room_reserve_invoice_rel', 'book_id', 'invoice_id', 'Room Reservation Invoices',readonly=True)
    untax_amt = fields.Float(compute=_get_untax_amt, string="Untaxed Amount", store=True)
    tax_amt = fields.Float(compute=_get_tax_amt,string="Taxes ", store=True)
    total_amt = fields.Float(compute=_get_total_amt, string="Total", store=True)
    state = fields.Selection([
                               ('draft', 'Draft'),
                               ('confirm', 'Confirm'),
                               ('checkout', "Checkout"),
                               ('cancel', 'Canceled'),
                               ('done', 'Done')
                               ], 
                               string='Status',
                               default=lambda * a: 'draft'
                            )
                                

#     _defaults = {
#                  'state': lambda * a: 'draft',
#                  }
    
    @api.multi
    def check_availability(self):
        for obj in self:
            if not obj.room_line_ids:
                raise UserError(' Please ADD Room Line Before Confirm')
            else:
                for i in range(0,len(obj.room_line_ids)):
                    if obj.room_line_ids[i].state == 'draft':
                        raise UserError(' Please Book The Room Before Confirm')
            if obj.adult + obj.child == 0:
                raise UserError(' Please Enter Details of Person like Adults And Child ')
            if obj.checkin_date > obj.checkout_date:
                raise UserError(' Please Check The Check out Date Which Is Less Than Check In Date')    
        self.write({'state':'confirm'})
        return True
    
#     def check_availability(self, cr, uid, ids, *args):
#         for obj in self.browse(cr,uid,ids):
#             if not obj.room_line_ids:
#                 raise osv.except_osv(_('Error !'), _(' Please ADD Room Line Before Confirm'))
#             else:
#                 for i in range(0,len(obj.room_line_ids)):
#                     if obj.room_line_ids[i].state == 'draft':
#                         raise osv.except_osv(_('Error !'), _(' Please Book The Room Before Confirm'))
#             if obj.adult + obj.child == 0:
#                 raise osv.except_osv(_('Error !'), _(' Please Enter Details of Person like Adults And Child '))
#             if obj.checkin_date > obj.checkout_date:
#                 raise osv.except_osv(_('Error !'), _(' Please Check The Check out Date Which Is Less Than Check In Date'))    
#         self.write(cr, uid, ids, {'state':'confirm'})
#         return True
    
    
    @api.multi
    def create_invoice(self):
        for obj in self:
            acc_id = obj.customer_id.property_account_receivable.id
            journal_ids = self.env['account.journal'].search([('type', '=','sale')], limit=1)
            type = 'out_invoice' 
            inv = {
                        'name': obj.name,
                        'origin': obj.name,
                        'type': type,
                        'reference': "Hotel Room Reservation",
                        'account_id': acc_id,
                        'partner_id': obj.customer_id.id,
                        'currency_id': self.env['res.currency'].search([('name', '=','EUR')])[0].id,
                        'journal_id': len(journal_ids) and journal_ids[0].id or False,
                        'amount_tax':obj.tax_amt,
                        'amount_untaxed':obj.untax_amt,
                        'amount_total':obj.total_amt,
                        }
            inv_id = self.env['account.invoice'].create(inv)
            tax = []
            for i in obj.tax_id:
                tax.append(i.id)
            il = {
                    'name': obj.name,
                    'account_id': obj.hotel_id.hotel_recv_acc.id,
                    'price_unit':obj.untax_amt , 
                    'quantity': 1.0,
                    'uos_id':  False,
                    'origin':obj.name,
                    'invoice_id':inv_id.id,
                    'pay_date':obj.current_date,
                    'order_amt':obj.untax_amt,
                    'invoice_line_tax_id':[(6,0,tax)],
                    }
            self.env['account.invoice.line'].create(il)
            self._cr.execute('insert into room_reserve_invoice_rel(book_id,invoice_id) values (%s,%s)', (obj.id, inv_id.id))
        self.write({'state':'checkout'})
        return True
    
    
#     def create_invoice(self, cr, uid, ids, *args):
#         for obj in self.browse(cr,uid,ids):
#             
#             acc_id = obj.customer_id.property_account_receivable.id
#             journal_obj = self.pool.get('account.journal')
#             journal_ids = journal_obj.search(cr, uid, [('type', '=','sale')], limit=1)
#             type = 'out_invoice' 
#             inv = {
#                         'name': obj.name,
#                         'origin': obj.name,
#                         'type': type,
#                         'reference': "Hotel Room Reservation",
#                         'account_id': acc_id,
#                         'partner_id': obj.customer_id.id,
# #                        'address_invoice_id': address_invoice_id[0] or False,
#                         'currency_id': self.pool.get('res.currency').search(cr, uid, [('name', '=','EUR')])[0],
#                         'journal_id': len(journal_ids) and journal_ids[0] or False,
#                         'amount_tax':obj.tax_amt,
#                         'amount_untaxed':obj.untax_amt,
#                         'amount_total':obj.total_amt,
#                         }
#             print("inv",inv)
#             inv_id = self.pool.get('account.invoice').create(cr, uid, inv)
#             print("tax_id",obj.tax_id)
#             tax = []
#             for i in obj.tax_id:
#                 tax.append(i.id)
#             il = {
#                     'name': obj.name,
#                     'account_id': obj.hotel_id.hotel_recv_acc.id,
#                     'price_unit':obj.untax_amt , 
#                     'quantity': 1.0,
#                     'uos_id':  False,
#                     'origin':obj.name,
#                     'invoice_id':inv_id,
#                     'pay_date':obj.current_date,
#                     'order_amt':obj.untax_amt,
#                     'invoice_line_tax_id':[(6,0,tax)],
#                     }
#             print("il",il)
#             self.pool.get('account.invoice.line').create(cr, uid, il,)
#             cr.execute('insert into room_reserve_invoice_rel(book_id,invoice_id) values (%s,%s)', (obj.id, inv_id))
# #        print asd    
#         self.write(cr, uid, ids, {'state':'checkout'})
#         return True
    

class room_info(models.Model):
    _name = "room.info"
    _description = "Room Information"
    
    name = fields.Char("Description",size=50,required=True)
    room_type_id = fields.Many2one('room.type','Room Type',required=True,)
    hotel_id = fields.Many2one('hotel.information','Hotel')
    book_id = fields.Many2one('hotel.reservation','Hotel Book ID')
    cost_price = fields.Float("Cost Price",required=True)
    sale_price = fields.Float("Sale Price",required=True)
    
    _sql_constraints = [
        ('room_type_id', 'unique (room_type_id,hotel_id)', 'You can not select same room type for selected hotel !'),
    ]
    
    
    @api.onchange('room_type_id')
    def on_change_room_type(self):
        result = {}
        if self.room_type_id:
            result['name'] = self.room_type_id.name
        return {'value': result}
    
#     def on_change_room_type(self,cr,uid,ids,room_type_id):
#         result = {}
#         print(room_type_id,"room_type_id",ids,"on_change_room_type")
#         if room_type_id:
#             obj = self.pool.get('room.type').browse(cr,uid,room_type_id)
#             result['name'] = obj.name
#         return {'value': result}
    
    
    @api.model
    def create(self, vals): 
        # function overwrites create method and auto generate request no. 
        so = super(room_info, self).create(vals)
        room_type_browse = self.env['room.type'].browse(vals['room_type_id'])
        hotel_browse = self.env['hotel.information'].browse(vals['hotel_id'])
        supplier_id = self.env['product.supplierinfo'].create({
                                                                   'name': hotel_browse.hotel_id.id,
                                                                   'min_qty': 1,
                                                                   'product_tmpl_id': room_type_browse.room_type.product_tmpl_id.id,
                                                                   'sale_price': vals['sale_price'],
                                                                   'price': vals['cost_price'],
                                                                })
        return so
    
#     def create(self, cr, uid, vals, context=None): 
#         # function overwrites create method and auto generate request no. 
#         so = super(room_info, self).create(cr, uid, vals, context=context)
#         room_type_browse = self.pool.get('room.type').browse(cr,uid,vals['room_type_id'])
#         hotel_browse = self.pool.get('hotel.information').browse(cr,uid,vals['hotel_id'])
#         supplier_id = self.pool.get('product.supplierinfo').create(cr, uid, {
#                                                                                'name': hotel_browse.hotel_id.id,
#                                                                                'min_qty': 1,
#                                                                                'product_tmpl_id': room_type_browse.room_type.product_tmpl_id.id,
#                                                                                'sale_price': vals['sale_price'],
#                                                                                'price': vals['cost_price'],
#                                                                                })
#         return so
    
    
    @api.multi
    def write(self, vals):
        """
        Overriding the write method
        """
        for obj in self:
            if 'room_type_id' in vals and vals['room_type_id'] and (vals['room_type_id'] != obj.room_type_id.id):
                raise Warning('Do not change room type.')
            if 'cost_price' in vals and vals['cost_price'] and (vals['cost_price'] != obj.cost_price):
                price_list = self.env['product.supplierinfo'].search([('name', '=', obj.hotel_id.hotel_id.id),('product_tmpl_id', '=', obj.room_type_id.room_type.id)])
                for prc_lst in price_list:
                    prc_lst.write({'price': vals['cost_price']})
            if 'sale_price' in vals and vals['sale_price'] and (vals['sale_price'] != obj.sale_price):
                price_list = self.env['product.supplierinfo'].search([('name', '=', obj.hotel_id.hotel_id.id),('product_tmpl_id', '=', obj.room_type_id.room_type.id)])
                for prc_lst in price_list:
                    prc_lst.write({'sale_price':vals['sale_price']})
        return super(room_info, self).write(vals)
    
#     def write(self, cr, uid, ids, vals, context=None):
#         """
#         Overriding the write method
#         """
#         for obj in self.browse(cr, uid, ids):
#             print(obj.hotel_id.hotel_id,"obj.hotel_id.hotel_id")
#             if 'room_type_id' in vals and vals['room_type_id'] and (vals['room_type_id'] != obj.room_type_id.id):
#                 raise osv.except_osv(_('Error !'), _('Do not change room type.'))
# #            visa_id = self.pool.get('product.product').search(cr, uid, [('name', '=', 'Visa'),('type', '=', 'service'),('categ_id', '=', 5)])
#             if 'cost_price' in vals and vals['cost_price'] and (vals['cost_price'] != obj.cost_price):
#                 price_list = self.pool.get('product.supplierinfo').search(cr, uid, [('name', '=', obj.hotel_id.hotel_id.id),('product_tmpl_id', '=', obj.room_type_id.room_type.id)])
# #                 price_list_val = self.pool.get('pricelist.partnerinfo').search(cr, uid, [('suppinfo_id', '=', price_list[0])])
# #                 print price_list,"price_list-------------"
#                 if price_list:
#                     self.pool.get('product.supplierinfo').write(cr, uid, price_list[0], {'price': vals['cost_price']})
#             if 'sale_price' in vals and vals['sale_price'] and (vals['sale_price'] != obj.sale_price):
#                 price_list = self.pool.get('product.supplierinfo').search(cr, uid, [('name', '=', obj.hotel_id.hotel_id.id),('product_tmpl_id', '=', obj.room_type_id.room_type.id)])
# #                 price_list_val = self.pool.get('pricelist.partnerinfo').search(cr, uid, [('suppinfo_id', '=', price_list[0])])
#                 if price_list:
#                     self.pool.get('product.supplierinfo').write(cr, uid, price_list[0], {'sale_price':vals['sale_price']})
#         return super(room_info, self).write(cr, uid, ids, vals, context=context)   
    


class hotel_service(models.Model):
    _name = "hotel.service"
    _description = "Hotel Service Configuration"
    
    name = fields.Char("Description",size=50,required=True)
    hotel_id1 = fields.Many2one('hotel.information','Hotel')
    book_id = fields.Many2one('hotel.reservation','Hotel Book ID')
    service_id = fields.Many2one("service.type","Service",required=True)
    cost_price = fields.Float("Cost Price",required=True)
    product_uom = fields.Many2one('uom.uom', 'Product UoM',required=True)
    state = fields.Selection([('draft', 'Draft'), ('available', 'Available'), ('done', 'Not Available')], string='Status',default=lambda *a: "draft")
    
    
    @api.onchange('service_id')
    def on_change_service_id(self):
        result = {}
        result['cost_price'] = self.service_id.service_id.standard_price
        result['product_uom'] = self.service_id.service_id.uom_id.id
        result['name'] = self.service_id.name
        return {'value': result}
    
#     def on_change_service_id(self,cr,uid,ids,service_id):
#         result = {}
#         
#         serv_obj = self.pool.get('service.type').browse(cr,uid,service_id)
#         prod_obj = self.pool.get('product.template').browse(cr,uid,serv_obj.service_id.id)
#         print("prod_obj",prod_obj)
#         print("prod_obj unit",prod_obj.uom_id.id,prod_obj.description)
#         result['cost_price'] = prod_obj.standard_price
#         result['product_uom'] = prod_obj.uom_id.id
#         result['name'] = serv_obj.name
#         return {'value': result}
    
    
#     _defaults = {
#                  "state": lambda *a: "draft",
#                  }
    


class room_line(models.Model):
    _name = "room.line"
    _description = "Room Line"
    
    @api.model
    def create(self,vals): 
        # function overwrites create method. 
        print("vals",vals)
        obj = self.env['room.info'].browse(vals['room_type_id'])
        if obj.available_rooms < vals['required_rooms']:
            raise Warning("Please Check Rooms Not Available !!!")
        return super(room_line, self).create(vals)
    
#     def create(self, cr, uid, vals, context=None): 
#         # function overwrites create method. 
#         print("vals",vals)
#         obj = self.pool.get('room.info').browse(cr,uid,vals['room_type_id'])
#         print("available rooms",obj.available_rooms)
#         if obj.available_rooms < vals['required_rooms']:
#             raise osv.except_osv(_("Warnning"),_("Please Check Rooms Not Available !!!"))
#         return super(room_line, self).create(cr, uid, vals, context=context)
    
    
    
    
    
    name = fields.Char("Name",size=50,required=True)
    room_type_id = fields.Many2one('room.info',"Room Type")
    available_rooms = fields.Float("Available Rooms")
    required_rooms = fields.Float("Required Rooms")
    days_required = fields.Float("Number Of Days",default=lambda self: self._get_default_days())
    room_cost = fields.Float("Rent")
    total_price = fields.Float("Total Price")
    book_id = fields.Many2one('hotel.reservation','Book ID')
    state = fields.Selection([
                           ('draft', 'Draft'),
                           ('book', 'Book'),
                           ('checked','Checked'),
                           ('cancel', 'Not Available'),
                           ('done', 'Done')
                           ],
                            string='Status',
                            readonly=True,
                            default=lambda *a: 'draft')
                           
    
    @api.onchange('room_type_id')
    def on_change_room_type_id(self):
        result = {}
        result['name'] = self.room_type_id.name
        result['room_cost'] = self.room_type_id.cost_price
        result['available_rooms'] = self.room_type_id.available_rooms
        return {'value': result}
                           
#     def on_change_room_type_id(self,cr,uid,ids,room_type_id):
#         result = {}
#         room_obj = self.pool.get('room.info').browse(cr,uid,room_type_id)
#         result['name'] = room_obj.name
#         result['room_cost'] = room_obj.cost_price
#         result['available_rooms'] = room_obj.available_rooms
#         return {'value': result}
    
    @api.onchange('required_rooms','room_cost','days_required')
    def on_change_required_rooms(self):
        result = {}
        result['total_price'] = self.required_rooms * self.room_cost * self.days_required
        return {'value': result}
    
#     def on_change_required_rooms(self,cr,uid,ids,required_rooms,room_cost,days_required):
#         result = {}
#         result['total_price'] = required_rooms * room_cost * days_required
#         return {'value': result}
  
     
    def _get_default_days(self):
        print("cotext",self._context)
        res = False
        if self._context is None:
            context = {}
        if 'parent_id' in self._context:
            rec=self.env['hotel.reservation'].browse(context['parent_id'])
            from_dt = time.mktime(time.strptime(rec.checkin_date,'%Y-%m-%d'))
            to_dt = time.mktime(time.strptime(rec.checkout_date,'%Y-%m-%d'))
            diff_day = (to_dt-from_dt)/(3600*24)
            res = round(diff_day)
        return res
     
#     def _get_default_days(self, cr, uid, context=None):
#         print("cotext",context)
#         res = False
#         if context is None:
#             context = {}
#         if 'parent_id' in context:
#             print('active_id',context['parent_id'])
#             rec=self.pool.get('hotel.reservation').browse(cr,uid,context['parent_id'])
#             print("checkindate",rec.checkin_date)
#             from_dt = time.mktime(time.strptime(rec.checkin_date,'%Y-%m-%d'))
#             print("from_dt",from_dt)
#             to_dt = time.mktime(time.strptime(rec.checkout_date,'%Y-%m-%d'))
#             diff_day = (to_dt-from_dt)/(3600*24)
#             res = round(diff_day)
#         return res 
    
    
    @api.multi
    def check_availability(self):
        tot_room = 0
        for obj in self:
            tot_room = obj.room_type_id.available_rooms - obj.required_rooms
            obj.room_type_id.write({'available_rooms':tot_room})
        self.write({'state':'book'})
        return True
    
#     def check_availability(self, cr, uid, ids, *args):
#         tot_room = 0
#         for obj in self.browse(cr,uid,ids):
#             print("hotel Id",obj.room_type_id.hotel_id.room_info_ids)
#             print("available_rooms",obj.room_type_id.available_rooms)
#             tot_room = obj.room_type_id.available_rooms - obj.required_rooms
#             self.pool.get('room.info').write(cr, uid, obj.room_type_id.id, {'available_rooms':tot_room})
#         self.write(cr, uid, ids, {'state':'book'})
#         return True
    
#     _defaults = {
#                  'days_required':lambda self,cr,uid,ctx: self._get_default_days(cr, uid, ctx),
#                  'state': lambda *a: 'draft',
#                  }
        

class service_line(models.Model):
    _name = "service.line"
    
    _description = "Service Line"
    
    name = fields.Char("Name",size=50,required=True)
    service_id = fields.Many2one('hotel.service',"Service",required=True)
    qty = fields.Float("Quantity",default=lambda *a: 1)
    room_cost = fields.Float("Rent")
    total_price = fields.Float("Total Price")
    book_id = fields.Many2one('hotel.reservation','Book ID')
    state = fields.Selection([
                               ('draft', 'Draft'),
                               ('available', 'Available'),
                               ('cancel', 'Not Available'),
                               ('done', 'Done')
                               ], 'Status',readonly=True)
    
    
    @api.onchange('service_id')
    def on_change_service_id(self):
        result = {}
        result['name'] = self.service_id.name
        result['room_cost'] = self.service_id.cost_price
        result['total_price'] = 1 * self.service_id.cost_price
        return {'value': result}
    
#     def on_change_service_id(self,cr,uid,ids,service_id):
#         result = {}
#         serv_obj = self.pool.get('hotel.service').browse(cr,uid,service_id)
#         result['name'] = serv_obj.name
#         result['room_cost'] = serv_obj.cost_price
#         result['total_price'] = 1 * serv_obj.cost_price
#         return {'value': result}
    
#     _defaults = {
#                  'qty':lambda *a: 1,
#                  }


