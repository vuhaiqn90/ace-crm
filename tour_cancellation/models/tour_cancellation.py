import time
from odoo import fields, models, api
from odoo.tools.translate import _
from datetime import datetime, timedelta
from odoo.exceptions import UserError,Warning


def get_price(self, pricelist_ids,price,context=None):
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
        price=currency_obj.compute(price, pricelist_obj.currency_id.id, round=False)
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

    price_amt=priceget_vals
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
#     
#     
#     
#     cr.execute(
#                 'SELECT i.* '
#                 'FROM product_pricelist_item AS i '
#                 'WHERE id = '+str(plversion_ids[0])+'')
#     
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


class tour_cancellation(models.Model):
    _name = "tour.cancellation"
    _description = "Tour Cancellation"
    '''
    def create(self, cr, uid, vals, context=None): 
        # function overwrites create method and auto generate request no. 
        req_no = self.pool.get('ir.sequence').get(cr,uid,'tour.cancellation'),
        vals['name'] = req_no[0]
        print
        print vals,"vals++++++++++++"
        return super(tour_cancellation, self).create(cr, uid, vals, context=context)
    '''
    
    @api.model
    def create(self, vals):
        result = {}
        if 'tour_customer_ids' in vals and vals['tour_customer_ids']:
            vals['tour_customer_ids'] = []
        if 'insurance_line_ids' in vals and vals['insurance_line_ids']:
            vals['insurance_line_ids'] = []
        if 'tour_sale_order_ids' in vals and vals['tour_sale_order_ids']:
            vals['tour_sale_order_ids'] = []
        if 'tour_booking_invoice_ids' in vals and vals['tour_booking_invoice_ids']:
            vals['tour_booking_invoice_ids'] = []
            
        res = super(tour_cancellation, self).create(vals)
        result = res.get_vals(vals['tour'])
        res.write(result)
        return res
    
#     def create(self, cr, uid, vals, context=None, *args, **kwargs):
#         result = {}
#         if  vals.has_key('tour_customer_ids') and vals['tour_customer_ids']:
#             vals['tour_customer_ids'] = []
#         if  vals.has_key('insurance_line_ids') and vals['insurance_line_ids']:
#             vals['insurance_line_ids'] = []
#             
#         if  vals.has_key('tour_sale_order_ids') and vals['tour_sale_order_ids']:
#             vals['tour_sale_order_ids'] = []
#             
#         if  vals.has_key('tour_booking_invoice_ids') and vals['tour_booking_invoice_ids']:
#             vals['tour_booking_invoice_ids'] = []
#             
#         res = super(tour_cancellation, self).create(cr, uid, vals, context=context)
#         result = self.get_vals(cr, uid,vals['tour'],res)
#         self.write(cr,uid,[res],result)
#         
#         return res
    
    
    @api.multi
    def get_vals(self,tour):
        print("hjhjjhhjjjjjjjjjjjjjjjjjjjjjjjjjjjj")
        result = {}
        if tour :
            trans_obj = self.env['tour.booking'].browse(tour)
            print (trans_obj,"trans_obj")
            result['tour_dates_id'] = trans_obj.tour_dates_id.id
            result['current_date'] = trans_obj.current_date
            result['pricelist_id'] = trans_obj.pricelist_id.id
            result['customer_id'] = trans_obj.customer_id.id
            result['email_id'] = trans_obj.email_id
            result['mobile1'] = trans_obj.mobile1
            result['adult'] = trans_obj.adult
            result['child'] = trans_obj.child
            result['tour_type'] = trans_obj.tour_type
            result['via'] = trans_obj.via
            result['season_id'] = trans_obj.season_id.id
            result['agent_id'] = trans_obj.agent_id.id
            result['tour_id'] = trans_obj.tour_id.id
            result['payment_policy_id'] = trans_obj.payment_policy_id.id
            result['adult_coverage'] = trans_obj.adult_coverage
            result['child_coverage1'] = trans_obj.child_coverage1
            result['total_amt'] = trans_obj.total_amt
            result['total_insurance_amt'] = trans_obj.total_insurance_amt
            
            req_no = self.env['ir.sequence'].get('tour.cancellation')
            result['name'] = req_no
           
            for customer in trans_obj.tour_customer_ids:
                
                create_result = {}
                create_result['tour_cancel_id'] = self.id
                create_result['name'] = customer.name
                create_result['partner_id'] = customer.partner_id.id
                create_result['gender'] = customer.gender
                create_result['type'] = customer.type
                create_result['h_flag'] = customer.h_flag
                create_result['t_flag'] = customer.t_flag
                create_result['i_flag'] = customer.i_flag
                create_result['v_flag'] = customer.v_flag
                create_result['p_flag'] = customer.p_flag
                create_result['customer_id'] = customer.customer_id
                create_result['state'] = customer.state
                print (create_result,"create_result customer details*******")
                self.env['tour.customer.details'].create(create_result)
                
                del create_result
                
            
            
            for insurance in trans_obj.insurance_line_ids:
                create_result = {}
                print (insurance,"insurance")
                create_result['tour_cancel_id'] = self.id
                create_result['insurance_policy_id'] = insurance.insurance_policy_id.id
                create_result['child_coverage1'] = insurance.child_coverage1
                create_result['insurance_cost'] = insurance.insurance_cost
                create_result['name'] = insurance.name
                self.env['tour.insurance.line'].create(create_result)
                
                del create_result
                            
            for so in trans_obj.tour_sale_order_ids:
                self._cr.execute('insert into tour_sale_order_cancel_rel(tour_book_id,sale_order_id) values (%s,%s)', (self.id, so.id))
                
            for invoice in trans_obj.tour_booking_invoice_ids:
                self._cr.execute('insert into tour_booking_invoice_cancel_rel(tour_booking_id,invoice_id) values (%s,%s)', (self.id, invoice.id))
            print("result----------------------------",result)
            
        return result
    
#     def get_vals(self, cr, uid,tour,res):
#         print tour,"in get_vals***************"
#         result = {}
#         if tour :
#             trans_obj = self.pool.get('tour.booking').browse(cr,uid,tour)
#             print trans_obj,"trans_obj"
#             result['tour_dates_id'] = trans_obj.tour_dates_id.id
#             result['current_date'] = trans_obj.current_date
#             result['pricelist_id'] = trans_obj.pricelist_id.id
#             result['customer_id'] = trans_obj.customer_id.id
# #            result['address_id'] = trans_obj.address_id.id
#             result['email_id'] = trans_obj.email_id
#             result['mobile1'] = trans_obj.mobile1
#             result['adult'] = trans_obj.adult
#             result['child'] = trans_obj.child
#             result['tour_type'] = trans_obj.tour_type
#             result['via'] = trans_obj.via
#             result['season_id'] = trans_obj.season_id.id
#             result['agent_id'] = trans_obj.agent_id.id
#             result['tour_id'] = trans_obj.tour_id.id
#             result['payment_policy_id'] = trans_obj.payment_policy_id.id
#             result['adult_coverage'] = trans_obj.adult_coverage
#             result['child_coverage1'] = trans_obj.child_coverage1
# #             result['tour_cost'] = trans_obj.tour_cost
#             result['total_amt'] = trans_obj.total_amt
#             result['total_insurance_amt'] = trans_obj.total_insurance_amt
# #            result['state'] = trans_obj.state
# #            result['state'] = "draft"
#             
#             req_no = self.pool.get('ir.sequence').get(cr,uid,'tour.cancellation'),
#             print 
#             result['name'] = req_no[0]
#            
#             #insurance_list = []
#             
#             
#             id_list = []
#             
#             for customer in trans_obj.tour_customer_ids:
#                 
#                 create_result = {}
#                 create_result['tour_cancel_id'] = res
#                 create_result['name'] = customer.name
#                 create_result['partner_id'] = customer.partner_id.id
#                 create_result['gender'] = customer.gender
#                 create_result['type'] = customer.type
#                 create_result['h_flag'] = customer.h_flag
#                 create_result['t_flag'] = customer.t_flag
#                 create_result['i_flag'] = customer.i_flag
#                 create_result['v_flag'] = customer.v_flag
#                 create_result['p_flag'] = customer.p_flag
#                 create_result['customer_id'] = customer.customer_id
#                 create_result['state'] = customer.state
#                 print create_result,"create_result customer details*******"
#                 self.pool.get('tour.customer.details').create(cr,uid,create_result)
#                 
#                 del create_result
#                 
#             
#             
#             for insurance in trans_obj.insurance_line_ids:
#                 create_result = {}
#                 print insurance,"insurance"
#                 print res, "res in get"
#                 create_reget_valssult['tour_cancel_id'] = res
#                 create_result['insurance_policy_id'] = insurance.insurance_policy_id.id
#                 create_result['child_coverage1'] = insurance.child_coverage1
#                 create_result['insurance_cost'] = insurance.insurance_cost
#                 create_result['name'] = insurance.name
#                 print create_result,"create_result*******"
#                 self.pool.get('tour.insurance.line').create(cr,uid,create_result)
#                 
#                 del create_result
#                             
#             for so in trans_obj.tour_sale_order_ids:
#                 cr.execute('insert into tour_sale_order_cancel_rel(tour_book_id,sale_order_id) values (%s,%s)', (res, so.id))
#                 
#             for invoice in trans_obj.tour_booking_invoice_ids:
#                 cr.execute('insert into tour_booking_invoice_cancel_rel(tour_booking_id,invoice_id) values (%s,%s)', (res, invoice.id))
#             
#         return result
    
    
    def _get_total_amt(self):
        res = {}
        total = 0
        obj = self[0]
        tour_cost = self._get_tour_cost()
        insurance_cost = self._get_insurance_total_amt()
        total = tour_cost.values()[0] + insurance_cost.values()[0]
        res[obj.id] = total 
        return res
    
#     def _get_total_amt(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         total = 0
#         obj = self.browse(cr, uid, ids)[0]
#         tour_cost = self._get_tour_cost(cr,uid,ids,args1,args2,context=context)
#         insurance_cost = self._get_insurance_total_amt(cr,uid,ids,args1,args2,context=context)
#         total = tour_cost.values()[0] + insurance_cost.values()[0]
#         #         total = obj.tour_cost + obj.total_insurance_amt
#         res[obj.id] = total 
#         return res
    
    
    def _get_tour_cost(self):
        res = {}
        total = 0
        person = 0
        tour_cost = 0.00
        adult_tour_cost = 0.0
        child_tour_cost = 0.0
        for obj in self:
            if obj.pricelist_id: 
                if obj.tour_id:
                    for tour_line in obj.tour_id.tour_date_lines:
                        if tour_line.id == obj.tour_dates_id.id:
                            adult_tour_cost = get_price(self, obj.pricelist_id.id, tour_line.adult_cost_price)
                            child_tour_cost = get_price(self, obj.pricelist_id.id, tour_line.child_cost_price)
                    adult_person = obj.adult 
                    child_person = obj.child
                    tour_cost = (adult_person * adult_tour_cost) + (child_person * child_tour_cost)
                else:
                    for tour_line in obj.tour.tour_id.tour_date_lines:
                        if tour_line.id == obj.tour.tour_dates_id.id:
                            adult_tour_cost = get_price(self, obj.pricelist_id.id, tour_line.adult_cost_price)
                            child_tour_cost = get_price(self, obj.pricelist_id.id, tour_line.child_cost_price)
                    adult_person = obj.adult 
                    child_person = obj.child
                    tour_cost = (adult_person * adult_tour_cost) + (child_person * child_tour_cost)
            total = tour_cost
            res[obj.id] = total
        return res
    
#     def _get_tour_cost(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         total = 0
#         person = 0
#         tour_cost = 0.00
#         adult_tour_cost = 0.0
#         child_tour_cost = 0.0
#         for obj in self.browse(cr, uid, ids):
#             print obj.tour,"obj.tour"
#             print obj,"obj",obj.tour_id,"obj.tour_id"
#             if obj.pricelist_id: 
#                 if obj.tour_id:
#                     print obj.tour_id,"obj.tour_id"
#                     for tour_line in obj.tour_id.tour_date_lines:
#                         if tour_line.id == obj.tour_dates_id.id:
#                             adult_tour_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, tour_line.adult_cost_price)
#                             child_tour_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, tour_line.child_cost_price)
#                     adult_person = obj.adult 
#                     child_person = obj.child
#                     tour_cost = (adult_person * adult_tour_cost) + (child_person * child_tour_cost)
#                 else:
#                     print "elasss"
#                     print obj,"obj"
#                     print  obj.tour.tour_id,"obj.tour_id"
#                     print obj.pricelist_id,"obj.pricelist_id"
#                     for tour_line in obj.tour.tour_id.tour_date_lines:
#                         print tour_line,"tour_line"
#                         if tour_line.id == obj.tour.tour_dates_id.id:
#                             adult_tour_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, tour_line.adult_cost_price)
#                             child_tour_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, tour_line.child_cost_price)
#                     adult_person = obj.adult 
#                     child_person = obj.child
#                     tour_cost = (adult_person * adult_tour_cost) + (child_person * child_tour_cost)
#             print "tour_cost",tour_cost
#             total = tour_cost
#             res[obj.id] = total
#         return res
     

    def _get_insurance_total_amt(self):
        res = {}
        total = 0
        for obj in self:
            if obj.insurance_line_ids:
                for line in obj.insurance_line_ids:
                    adult_cost = get_price(self, obj.pricelist_id.id, line.insurance_policy_id.insurance_cost_for_adults)
                    child_cost = get_price(self,obj.pricelist_id.id, line.insurance_policy_id.insurance_cost_for_childs)
                    total = (adult_cost * line.name)  + (child_cost * line.child_coverage1)
                    if obj.adult < line.name:
                        raise UserError('Check Adult Persons For Policy Coverage ')
                    if obj.child < line.child_coverage1:
                        raise UserError('Check Child For Policy Coverage ')
                    res[obj.id] = total  
        res[obj.id] = total
        return res
    
#     def _get_insurance_total_amt(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         total = 0
#         for obj in self.browse(cr,uid,ids):
#             print obj.pricelist_id.id,"dddddddddddddddddddobj.pricelist_id.id================"
#             if obj.insurance_line_ids:
#                 for line in obj.insurance_line_ids:
#                     print obj.pricelist_id.id,"obj.pricelist_id.id==========================="
#                     adult_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, line.insurance_policy_id.insurance_cost_for_adults)
#                     child_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, line.insurance_policy_id.insurance_cost_for_childs)
#                     total = (adult_cost * line.name)  + (child_cost * line.child_coverage1)
#                     if obj.adult < line.name:
#                         raise osv.except_osv(_('Error !'), _('Check Adult Persons For Policy Coverage '))
#                     if obj.child < line.child_coverage1:
#                         raise osv.except_osv(_('Error !'), _('Check Child For Policy Coverage '))
#                 #                    total = total + line.insurance_cost 
#                     res[obj.id] = total  
#         res[obj.id] = total
#         return res
     
    
    @api.onchange('tour_id')
    def on_change_tour_id(self):
        print("kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
        result = {}
        trans_obj = self.tour
        result['tour_dates_id'] = trans_obj.tour_dates_id.id
        result['current_date'] = trans_obj.current_date
        result['pricelist_id'] = trans_obj.pricelist_id.id
        result['customer_id'] = trans_obj.customer_id.id
        result['email_id'] = trans_obj.email_id
        result['mobile1'] = trans_obj.mobile1
        result['adult'] = trans_obj.adult
        result['child'] = trans_obj.child
        result['tour_type'] = trans_obj.tour_type
        result['via'] = trans_obj.via
        result['season_id'] = trans_obj.season_id.id
        result['agent_id'] = trans_obj.agent_id.id
        result['tour_id'] = trans_obj.tour_id.id
        result['payment_policy_id'] = trans_obj.payment_policy_id.id
        result['adult_coverage'] = trans_obj.adult_coverage
        result['child_coverage1'] = trans_obj.child_coverage1
        result['tour_cost'] = trans_obj.tour_cost
        result['total_amt'] = trans_obj.total_amt
        result['total_insurance_amt'] = trans_obj.total_insurance_amt
        result['state'] = "draft"
        result['subtotal'] = trans_obj.subtotal
        result['tax_amt'] = trans_obj.tax_amt
                
        insurance_list = []
        for insurance in trans_obj.insurance_line_ids:
            insurance_list.append(insurance.id)            
        result['insurance_line_ids'] = insurance_list
        id_list = []
        for customer in trans_obj.tour_customer_ids:
            id_list.append(customer.id)            
        result['tour_customer_ids'] = id_list

        
        invoice_list = []
        for invoice in trans_obj.tour_booking_invoice_ids:
            invoice_list.append(invoice.id)
        result['tour_booking_invoice_ids'] = invoice_list
        
        so_list = []
        for so in trans_obj.tour_sale_order_ids:
            so_list.append(so.id)
        result['tour_sale_order_ids'] = so_list
        
        if self.id:
            raise Warning("Cannot change Tour Booking ID at this stage.")
        print("result========================",result)

        return {'value': result}
    
    
    
    
#     def on_change_tour_id(self,cr,uid,ids,tour_id):
#         result = {}
#          
#         print tour_id,"tour_id"
#         trans_obj = self.pool.get('tour.booking').browse(cr,uid,tour_id)
#         print trans_obj.tour_cost,'====================================dfdf'
#         print trans_obj,"trans_obj"
#         result['tour_dates_id'] = trans_obj.tour_dates_id.id
#         result['current_date'] = trans_obj.current_date
#         result['pricelist_id'] = trans_obj.pricelist_id.id
#         result['customer_id'] = trans_obj.customer_id.id
# #        result['address_id'] = trans_obj.address_id.id
#         result['email_id'] = trans_obj.email_id
#         result['mobile1'] = trans_obj.mobile1
#         result['adult'] = trans_obj.adult
#         result['child'] = trans_obj.child
#         result['tour_type'] = trans_obj.tour_type
#         result['via'] = trans_obj.via
#         result['season_id'] = trans_obj.season_id.id
#         result['agent_id'] = trans_obj.agent_id.id
#         result['tour_id'] = trans_obj.tour_id.id
#         result['payment_policy_id'] = trans_obj.payment_policy_id.id
#         result['adult_coverage'] = trans_obj.adult_coverage
#         result['child_coverage1'] = trans_obj.child_coverage1
#         result['tour_cost'] = trans_obj.tour_cost
#         result['total_amt'] = trans_obj.total_amt
#         result['total_insurance_amt'] = trans_obj.total_insurance_amt
# #        result['state'] = trans_obj.state
#         result['state'] = "draft"
#         result['subtotal'] = trans_obj.subtotal
#         result['tax_amt'] = trans_obj.tax_amt
#          
#                  
#         insurance_list = []
#         for insurance in trans_obj.insurance_line_ids:
# #            print insurance,"insurance"
#             insurance_list.append(insurance.id)            
#         result['insurance_line_ids'] = insurance_list
#         id_list = []
#         for customer in trans_obj.tour_customer_ids:
#             id_list.append(customer.id)            
#         result['tour_customer_ids'] = id_list
#  
#          
#         invoice_list = []
#         for invoice in trans_obj.tour_booking_invoice_ids:
#             invoice_list.append(invoice.id)
# #        result['tour_booking_invoice_ids'] = [(6,0,invoice_list)]
#         result['tour_booking_invoice_ids'] = invoice_list
#          
#         so_list = []
#         for so in trans_obj.tour_sale_order_ids:
# #            print so, "so--------------------"
#             so_list.append(so.id)
#         #result['tour_sale_order_ids'] = [(6,0,so_list)]
#         result['tour_sale_order_ids'] = so_list
#          
#         if ids:
#             raise osv.except_osv(_("Warning"),_("Cannot change Tour Booking ID at this stage."))
#  
#         print
#         print result,"result^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
#         return {'value': result}
    
    
    name = fields.Char("Tour Cancellation ID",size=50,readonly=True,states={'draft': [('readonly', False)]})
    tour = fields.Many2one('tour.booking',"Tour Booking ID",domain="[('state','in',('invoiced','done'))]",readonly=True,states={'draft': [('readonly', False)]})
    cancel_date = fields.Date("Tour Cancel Date",required=True,readonly=True,default=lambda *args: time.strftime('%Y-%m-%d'))
    current_date = fields.Date("Booking Date",readonly=True)
    customer_id = fields.Many2one('res.partner','Customer',readonly=True)
    email_id = fields.Char('Email Id',size=150,readonly=True)
    mobile1 = fields.Char('Mobile Number',size=200, readonly=True)
    adult = fields.Integer("Adult Persons",readonly=True)
    child = fields.Integer("Child",readonly=True)
    tour_type = fields.Selection([
                                    ('international','International'),
                                    ('domestic','Domestic')
                                    ],"Tour Type",readonly=True)
    via = fields.Selection([
                            ('direct','Direct'),
                            ('agent','Agent'),
                            ],"Via",readonly=True,default=lambda * a: 'direct')
    season_id = fields.Many2one('tour.season','Season',readonly=True)
    agent_id = fields.Many2one('res.partner','Agent',readonly=True)
    tour_id = fields.Many2one('tour.package',"Tour",readonly=True)
    tour_dates_id = fields.Many2one('tour.dates',"Tour Dates",readonly=True)
    payment_policy_id = fields.Many2one('tour.payment.policy',"Payment Policy",readonly=True)
    adult_coverage = fields.Integer("Number of Adult Persons Policy Coverage")
    child_coverage1 = fields.Integer("Number of Child Policy Coverage")
    insurance_line_ids = fields.One2many('tour.insurance.line','tour_cancel_id','Insurance Line',readonly=True,states={'draft': [('readonly', False)]})
    tour_customer_ids = fields.One2many('tour.customer.details','tour_cancel_id','Tour Customer Details',readonly=True,states={'draft': [('readonly', False)]})
    tour_booking_invoice_ids = fields.Many2many('account.invoice','tour_booking_invoice_cancel_rel', 'tour_booking_id', 'invoice_id', 'Tour Invoices',readonly=True)
    tour_sale_order_ids = fields.Many2many('sale.order','tour_sale_order_cancel_rel', 'tour_book_id', 'sale_order_id', 'Sales Orders',readonly=True)
    tour_cost = fields.Float(compute=_get_tour_cost, string="Tour Cost", store=True)
    total_amt = fields.Float(compute=_get_total_amt, string="Total Amount", store=True)
    total_insurance_amt = fields.Float(compute=_get_insurance_total_amt, string="Insurance Amount", store=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist',readonly=True, states={'draft': [('readonly', True)]})
    
    state = fields.Selection([
                               ('draft', 'Draft'),
                               ('in_process', 'In Process'),
                               ('done', 'Done'),
                               ], 'Status',readonly=True,default=lambda * a: 'draft')

    
#     _defaults = {
#                  'state': lambda * a: 'draft',
#                  'via': lambda * a: 'direct',
#                  'cancel_date':lambda *args: time.strftime('%Y-%m-%d'),
#                  }
    
    @api.multi
    def tour_cancel(self):
        return True
    
#     def tour_cancel(self, cr, uid, ids, *args):
#         print "pressed Cancel button..."
#         return True
    
    
    def button_request(self):
        objt = self[0]
        type_a = 0
        type_c = 0

        objs = self.env['tour.customer.details'].search([('tour_cancel_id', '=', objt.id)])
        for record in objs :
            obj = record
            if obj.type == "adult" :
                type_a = type_a + 1
            if obj.type == "child" :
                type_c = type_c + 1
                
        objs = self.env['tour.insurance.line'].search([('tour_cancel_id', '=', objt.id)])
        for record in objs :
            record.write({'name':type_a,'child_coverage1':type_c})
        self.write({'state':'in_process', 'adult':type_a,'child':type_c})
        
        return True
    
    #added
#     def button_request(self, cr, uid, ids, *args):
#         objt = self.browse(cr,uid,ids)
#         objt = objt[0]
#         type_a = 0
#         type_c = 0
# 
#         objs = self.pool.get('tour.customer.details').search(cr, uid, [('tour_cancel_id', '=', objt.id)])
#         for record in objs :
#             obj = self.pool.get('tour.customer.details').browse(cr,uid,record)
#             if obj.type == "adult" :
#                 type_a = type_a + 1
#             if obj.type == "child" :
#                 type_c = type_c + 1
#                 
#         objs = self.pool.get('tour.insurance.line').search(cr, uid, [('tour_cancel_id', '=', objt.id)])
#         for record in objs :
#             self.pool.get('tour.insurance.line').write(cr, uid, record, {'name':type_a,'child_coverage1':type_c})
#         self.write(cr, uid, ids, {'state':'in_process', 'adult':type_a,'child':type_c})
#         
#         return True
    
    @api.multi
    def button_done(self):
        return True

#     def button_done(self, cr, uid, ids, *args):
#         return True


class tour_customer_details(models.Model):
    _inherit = "tour.customer.details"
    _description = "Tour Customer Details "
    
    tour_cancel_id = fields.Many2one('tour.cancellation','Tour cancel ID')
    


class tour_insurance_line(models.Model):
    _inherit = "tour.insurance.line"
    _description = "Tour Insurance Lines"
    
    
    def _get_insurance_cost(self):
        res = {}
        obj = self[0]
        adult_cost = obj.insurance_policy_id.insurance_cost_for_adults * obj.name
        child_cost = obj.insurance_policy_id.insurance_cost_for_childs * obj.child_coverage1
        total = adult_cost + child_cost
        
        if obj.tour_book_id :
            res = super(tour_insurance_line, self)._get_insurance_cost()
            
        else :
            if obj.tour_cancel_id :
                if obj.tour_cancel_id.tour.adult < obj.name:
                    raise UserWarning('Check Adult Persons For Policy Coverage ')
                if obj.tour_cancel_id.tour.child < obj.child_coverage1:
                    raise UserWarning('Check Child For Policy Coverage ')
                res[obj.id] = total
            
        return res
    
#     def _get_insurance_cost(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         total = 0
#         adult_cost = 0
#         child_cost = 0
#         obj = self.browse(cr, uid, ids)[0]
# #        print obj, "obj"
#         adult_cost = obj.insurance_policy_id.insurance_cost_for_adults * obj.name
#         child_cost = obj.insurance_policy_id.insurance_cost_for_childs * obj.child_coverage1
#         total = adult_cost + child_cost
#         
#         if obj.tour_book_id :
#             res = super(tour_insurance_line, self)._get_insurance_cost(cr, uid, ids,args1,args2,context=context)
#             
#         else :
#             if obj.tour_cancel_id :
#                 if obj.tour_cancel_id.tour.adult < obj.name:
#                     raise osv.except_osv(_('Error !'), _('Check Adult Persons For Policy Coverage '))
#                 if obj.tour_cancel_id.tour.child < obj.child_coverage1:
#                     raise osv.except_osv(_('Error !'), _('Check Child For Policy Coverage '))
#                 res[obj.id] = total
#             
#         return res
    
    
    tour_cancel_id = fields.Many2one('tour.cancellation','Tour cancel ID')
    insurance_cost = fields.Float(compute=_get_insurance_cost,string="Total Cost", store=True)
    
    
