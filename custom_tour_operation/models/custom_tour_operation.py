import time
from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, Warning
from datetime import datetime, timedelta
from odoo.addons import decimal_precision as dp
import string



def get_price(self, pricelist_ids,price):
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
    if len(pricelist_item_ids) != len(plversion_ids):
        msg = "At least one pricelist has no active version !\nPlease create or activate one."
        raise Warning(msg)
    

    self._cr.execute(
                'SELECT i.* '
                'FROM product_pricelist_item AS i '
                'WHERE id = ' + str(plversion_ids[0].id) + '')
                
    res1 = self._cr.dictfetchall()
    if pricelist_obj:
        price=currency_obj.compute(price, pricelist_obj.currency_id, round=False)
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
#     if len(pricelist_item_ids) != len(plversion_ids):
#         msg = "At least one pricelist has no active version !\nPlease create or activate one."
#         raise osv.except_osv(_('Warning !'), _(msg))
#     
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
#     price_amt = price
#     return price_amt



# class crm_partner_binding(models.TransientModel):
#     _inherit = 'crm.partner.binding'
#     _description = 'Handle partner binding or generation in CRM wizards.'
#     
#     def default_get(self, cr, uid, fields, context=None):
#         print "default_get======================ccccccccccc========ggggggggggggggggggggggggg"
#         print fields,"fields==========================="
#         if 'action' in fields:
#             res['action'] = partner_id and 'exist' or 'create'
#         print res,"res==================="
#         return res



class crm_lead2opportunity_partner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'
    _description = 'Lead To Opportunity Partner'

    @api.model
    def default_get(self, fields):
        """
        Default get for name, opportunity_ids.
        If there is an exisitng partner link to the lead, find all existing
        opportunities links with this partner to merge all information together
        """
        res = {}
        if 'action' in fields:
            res.update({'action' :'create'})
        if 'name' in fields:
            res.update({'name' : 'convert'})
        return res
    
#     def default_get(self, cr, uid, fields, context=None):
#         """
#         Default get for name, opportunity_ids.
#         If there is an exisitng partner link to the lead, find all existing
#         opportunities links with this partner to merge all information together
#         """
#         lead_obj = self.pool.get('crm.lead')
#         print "default_get============================fields",fields
#         res = {}
#         print context,"context==================="
#         print res,"ressuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"
#         if 'action' in fields:
#             res.update({'action' :'create'})
#         if 'name' in fields:
#             res.update({'name' : 'convert'})
#         print res,"resssssssssssssssssssssssssssssssssssssssss"
#         return res



class tour_preference(models.Model):
    _name = "tour.preference"
    _description = "Tour Preference"
    
    
    @api.model
    def create(self, vals): 
        # function overwrites create method and auto generate request no. 
        req_no = self.env['ir.sequence'].get('tour.preference')
        vals['name'] = req_no
        lead_browse = self.env['crm.lead'].browse(vals.get('lead'))
        if (not lead_browse.email_from) and 'email_id' in vals and vals['email_id']:
            lead_browse.write({'email_from':vals['email_id']})
        if (not lead_browse.mobile) and 'mobile' in vals and vals['mobile']:
            lead_browse.write({'mobile':vals['mobile']})
        if (not lead_browse.contact_name) and 'contact_name' in vals and vals['contact_name']:
            lead_browse.write({'contact_name':vals['contact_name']})
        if (not lead_browse.country_id) and 'country_id' in vals and vals['country_id']:
            lead_browse.write({'country_id':vals['country_id']})
        return super(tour_preference, self).create(vals)
    
#     def create(self, cr, uid, vals, context=None): 
#         # function overwrites create method and auto generate request no. 
#         req_no = self.pool.get('ir.sequence').get(cr,uid,'tour.preference'),
#         vals['name'] = req_no[0]
#         lead_browse = self.pool.get('crm.lead').browse(cr,uid,vals['lead'])
#         print lead_browse,"address_browse"
#         if (not lead_browse.email_from) and vals.has_key('email_id') and vals['email_id']:
#             self.pool.get('crm.lead').write(cr,uid,lead_browse.id, {'email_from':vals['email_id']})
#         if (not lead_browse.mobile) and vals.has_key('mobile') and vals['mobile']:
#             self.pool.get('crm.lead').write(cr,uid,lead_browse.id, {'mobile':vals['mobile']})
#         if (not lead_browse.contact_name) and vals.has_key('contact_name') and vals['contact_name']:
#             self.pool.get('crm.lead').write(cr,uid,lead_browse.id, {'contact_name':vals['contact_name']})
#         if (not lead_browse.country_id) and vals.has_key('country_id') and vals['country_id']:
#             self.pool.get('crm.lead').write(cr,uid,lead_browse.id, {'country_id':vals['country_id']})
#         return super(tour_preference, self).create(cr, uid, vals, context=context)
    
    
    
    name = fields.Char("Enquiry No.",size=128,readonly=True)
    current_date = fields.Date("Enquiry Date",required=True,readonly=True, states={'draft': [('readonly', False)]},default=lambda *args: time.strftime('%Y-%m-%d'))
    lead = fields.Many2one('crm.lead','Lead',required=True,readonly=True, states={'draft': [('readonly', False)]},)
    contact_name = fields.Char('Contact Name',size=64,readonly=True, states={'draft': [('readonly', False)]},)
    address = fields.Char('Address',size=256,readonly=True, states={'draft': [('readonly', False)]},)
    email_id = fields.Char('Email Id',size=64,readonly=True, states={'draft': [('readonly', False)]},)
    mobile = fields.Char('Mobile Number',size=15, required=True,readonly=True, states={'draft': [('readonly', False)]},)
    adult = fields.Integer("Adult Persons",readonly=True, states={'draft': [('readonly', False)]},)
    child = fields.Integer("Child",readonly=True, states={'draft': [('readonly', False)]},)
    checkin_date = fields.Date("Prefer start Date",required=True,readonly=True, states={'draft': [('readonly', False)]})
    checkout_date = fields.Date("Prefer End Date",required=True,readonly=True, states={'draft': [('readonly', False)]},)
    country_id = fields.Many2one('res.country','Origin',required=True,readonly=True, states={'draft': [('readonly', False)]},)
    via = fields.Selection([('direct','Direct'),('agent','Agent')],"Via",readonly=True, states={'draft': [('readonly', False)]},default=lambda * a: 'direct')
    agent_id = fields.Many2one('res.partner','Agent',readonly=True, states={'draft': [('readonly', False)]},)
    destination_lines_ids = fields.One2many('custom.tour.destination','tour_pref_id','Sites',readonly=True, states={'draft': [('readonly', False)]},)
    hotel_type_id = fields.Many2one('hotel.type','Hotel Type',readonly=True, states={'draft': [('readonly', False)]},)
    room_type_id = fields.Many2one('product.product',"Room Type",readonly=True, states={'draft': [('readonly', False)]},)
    low_price = fields.Float("Price Limit (min/max)",readonly=True, states={'draft': [('readonly', False)]},)
    high_price = fields.Float("Price Limit (min/max)",readonly=True, states={'draft': [('readonly', False)]},)
    room_req = fields.Integer("No of Room Required",readonly=True, states={'draft': [('readonly', False)]},)
    transport_ids = fields.One2many('custom.tour.transport','tour_transport_id','Sites',readonly=True, states={'draft': [('readonly', False)]},)
    tour_low_price = fields.Float("Budget/ Person (min/max)",readonly=True, states={'draft': [('readonly', False)]},)
    tour_high_price = fields.Float("Budget/ Person (min/max)",readonly=True, states={'draft': [('readonly', False)]},)
    state = fields.Selection([
                               ('draft', 'Draft'),
                               ('confirm', 'Confirm'),
                               ('cancel', 'Cancel'),
                               ], 'Status',readonly=True,default=lambda * a: 'draft')
    
    
#     _defaults = {
#                  'state': lambda * a: 'draft',
#                  'via': lambda * a: 'direct',
#                  'current_date':lambda *args: time.strftime('%Y-%m-%d'),
#                  }
    
    _sql_constraints = [
        ('checkin_checkout_date', 'CHECK (checkout_date > checkin_date)',  "Preferred end date must be greater than Preferred start date !"),
    ]
    
    
    @api.onchange('lead')
    def on_change_lead_id(self):
        result = {}
        if self.lead:
            res = self.lead
            address = ''
            if res.street:
                address += res.street + ' '
            if res.street2:
                address += res.street2 + ' '
            if res.city:
                address += res.city + ' '
            if res.zip:
                address += res.zip + ' '
            result['address'] = address
            result['contact_name'] = res.contact_name
            result['mobile'] = res.mobile
            result['email_id'] = res.email_from   
            result['country_id'] = res.country_id.id
            result['via'] = res.via
            result['agent_id'] = res.agent_id.id
        return {'value': result}
    
#     def on_change_lead_id(self,cr,uid,ids,lead_id):
#         result = {}
#         if lead_id:
#             res = self.pool.get('crm.lead').browse(cr,uid,lead_id)
#             address = ''
#             if res.street:
#                 address += res.street + ' '
#             if res.street2:
#                 address += res.street2 + ' '
#             if res.city:
#                 address += res.city + ' '
#             if res.zip:
#                 address += res.zip + ' '
#             result['address'] = address
#             result['contact_name'] = res.contact_name
#             result['mobile'] = res.mobile
#             result['email_id'] = res.email_from   
#             result['country_id'] = res.country_id.id
#             result['via'] = res.via
#             result['agent_id'] = res.agent_id.id
#             print "result",result
#         return {'value': result}
    
    
    @api.multi
    def action_confirm(self):
        self.write({'state':'confirm'})
        return True
    
#     def action_confirm(self, cr, uid, ids, *args):
#         self.write(cr, uid, ids, {'state':'confirm'})
#         return True
    
    
    @api.multi
    def action_refuse(self):
        self.write({'state':'cancel'})
        return True
    
#     def action_refuse(self, cr, uid, ids, *args):
#         self.write(cr, uid, ids, {'state':'cancel'})
#         return True
    
    


class custom_tour_destination(models.Model):
    _name = "custom.tour.destination"
    _description = "Custom Tour Destination"
    
    
    @api.onchange('destination_id')
    def onchange_destination_id(self):
        result= {}
        if self.destination_id:
            result['country_id'] = self.destination_id.country_id.id     
        return {'value':result}
    
#     def onchange_destination_id(self,cr,uid,ids,destination_id):
#         result= {}
#         if destination_id:
#             obj = self.pool.get('tour.destinations').browse(cr,uid,destination_id)
#             result['country_id'] = obj.country_id.id     
#         return {'value':result}
    
    destination_id = fields.Many2one('tour.destinations','Destination',required=True)
    country_id = fields.Many2one('res.country','Country',required=True)
    name = fields.Integer('No. Of Nights',required=True)
    site_line_ids = fields.One2many('custom.tour.site','site_id','Sites')
    tour_pref_id = fields.Many2one('tour.preference','Destination',required=True)
 

class custom_tour_site(models.Model):
    _name = "custom.tour.site"
    _description = "Custom Tour Site"
    
    site_id = fields.Many2one('custom.tour.destination','Destination',required=True)
    name = fields.Many2one('product.product','Sites Name',required=True)
                
 

class custom_tour_transport(models.Model):
    _name = "custom.tour.transport"
    _description = "Custom Tour Transport"
    
    
    tour_transport_id = fields.Many2one('tour.preference','Destination Ref',required=True)
    name = fields.Selection([('destination','Between Destinations'),('site','Site Seeing')],"Location",required=True)
    transport_type_id = fields.Many2one('product.product','Transport Type',required=True)
    travel_class_id = fields.Many2one('travel.class','Travel Class',required=True)
                
 

class custom_tour_itinarary(models.Model):
    _name = "custom.tour.itinarary"
    _description = "Custom Tour Itinerary"
    
    
    @api.multi
    def unlink(self):
        """
        Allows to delete Product Category which are not defined in demo data
        """
        for rec in self:
            raise UserWarning('Cannot delete these Itinerary.!')
        return super(custom_tour_itinarary, self).unlink()
    
#     def unlink(self, cr, uid, ids, context):
#         """
#         Allows to delete Product Category which are not defined in demo data
#         """
#         for rec in self.browse(cr, uid, ids, context = context):
#             raise osv.except_osv(_('Invalid action !'), _('Cannot delete these Itinerary.!'))
#         return super(custom_tour_itinarary, self).unlink(cr, uid, ids, context = context)
    
    
    
    @api.model
    def create(self,vals):
        # function overwrites create method and auto generate request no.
        enq_browse = self.env['tour.preference'].browse(vals.get('tour_pref_id'))
        enq_name = enq_browse.name
        n = 1
        itinarary_browse_id = self.search([])
        if itinarary_browse_id:
            for itinararay in itinarary_browse_id:
                iti = itinararay.tour_pref_id.name
                if iti == enq_name:
                    n += 1
        n = str('%02d' % n)    
        iti_name = enq_name.upper() + '/' + n 
        vals['name'] = iti_name
        lead_browse = self.env['crm.lead'].browse(vals.get('lead'))
        print (lead_browse,"address_browse")
        if (not lead_browse.email_from) and 'email_id' in vals and vals['email_id']:
            lead_browse.write({'email_from':vals['email_id']})
        if (not lead_browse.mobile) and 'mobile' in vals and vals['mobile']:
            lead_browse.write({'mobile':vals['mobile']})
        if (not lead_browse.contact_name) and 'contact_name' in vals and vals['contact_name']:
            lead_browse.write({'contact_name':vals['contact_name']})
        if (not lead_browse.country_id) and 'country_id' in vals and vals['country_id']:
            lead_browse.write({'country_id':vals['country_id']})
        so = super(custom_tour_itinarary, self).create(vals)
        if enq_browse.destination_lines_ids:
            for destination in enq_browse.destination_lines_ids:
                destination_id = self.env['tour.destination.line'].create({
                                                                           'destination_id': destination.destination_id.id,
                                                                           'country_id': destination.country_id.id,
                                                                           'name': destination.name,
                                                                           'itinarary_id':so.id
                                                                        })
        return so
    
#     def create(self, cr, uid, vals, context=None): 
#         # function overwrites create method and auto generate request no. 
#         enq_browse = self.pool.get('tour.preference').browse(cr,uid,vals['tour_pref_id'])
#         enq_name = enq_browse.name
#         n = 1
#         itinarary_search_id = self.search(cr, uid, [])
#         itinarary_browse_id = self.browse(cr, uid, itinarary_search_id)
#         if itinarary_browse_id:
#             for itinararay in itinarary_browse_id:
#                 iti = itinararay.tour_pref_id.name
#                 if iti == enq_name:
#                     n += 1
#         n = str('%02d' % n)    
#         iti_name = string.upper(enq_name) + '/' + n 
#         vals['name'] = iti_name
#         lead_browse = self.pool.get('crm.lead').browse(cr,uid,vals['lead'])
#         print lead_browse,"address_browse"
#         if (not lead_browse.email_from) and vals.has_key('email_id') and vals['email_id']:
#             self.pool.get('crm.lead').write(cr,uid,lead_browse.id, {'email_from':vals['email_id']})
#         if (not lead_browse.mobile) and vals.has_key('mobile') and vals['mobile']:
#             self.pool.get('crm.lead').write(cr,uid,lead_browse.id, {'mobile':vals['mobile']})
#         if (not lead_browse.contact_name) and vals.has_key('contact_name') and vals['contact_name']:
#             self.pool.get('crm.lead').write(cr,uid,lead_browse.id, {'contact_name':vals['contact_name']})
#         if (not lead_browse.country_id) and vals.has_key('country_id') and vals['country_id']:
#             self.pool.get('crm.lead').write(cr,uid,lead_browse.id, {'country_id':vals['country_id']})
#         so = super(custom_tour_itinarary, self).create(cr, uid, vals, context=context)
#         if enq_browse.destination_lines_ids:
#             for destination in enq_browse.destination_lines_ids:
#                 print destination
#                 destination_id = self.pool.get('tour.destination.line').create(cr, uid, {
#                                                                                        'destination_id': destination.destination_id.id,
#                                                                                        'country_id': destination.country_id.id,
#                                                                                        'name': destination.name,
#                                                                                        'itinarary_id':so
#                                                                                        })
#         return so
    
    @api.depends('adult','child')
    def _get_total_seat(self):
        res = {}
        total = 0
        for obj in self:
            self.total_seat = obj.adult + obj.child

        return res
    
#     def _get_total_seat(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         total = 0
#         for obj in self.browse(cr, uid, ids):
#             total = obj.adult + obj.child
#         res[obj.id] = total
#         return res
     
    
    def _get_total_amt_pur(self):
        res = {}
        for obj in self:
            untax = obj._get_untax_amt_pur()
            tax_amt = obj._get_tax_amt_pur()
            res[obj.id] = untax[obj.id] + tax_amt[obj.id]
        return res
    
#     def _get_total_amt_pur(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         for obj in self.browse(cr, uid, ids):
#             untax = self._get_untax_amt_pur(cr, uid, [obj.id],args1,args2)
#             tax_amt = self._get_tax_amt_pur(cr, uid, [obj.id],args1,args2)
#             res[obj.id] = untax[obj.id] + tax_amt[obj.id]
#         return res
    
    
    def _get_tax_amt_pur(self):
        res = {}
        total = 0.00
        for obj in self:
            for service in obj.service_ids:
                for tax_line in service.pur_tax_ids:
                    if tax_line.amount_type == 'percent':
                        total += tax_line.amount * service.price_subtotal_cost
                    else:
                        total += tax_line.amount
            for site in obj.sites_costing_ids:
                for tax_line in site.pur_tax_ids:
                    if tax_line.amount_type == 'percent':
                        total += tax_line.amount * site.total_cost_price
                    else:
                        total += tax_line.amount
            for visa in obj.visa_costing_ids:
                for tax_line in visa.pur_tax_ids:
                    if tax_line.amount_type == 'percent':
                        total += tax_line.amount * visa.total_cost_price
                    else:
                        total += tax_line.amount
            for hotel in obj.hotel_planer_ids:
                for tax_line in hotel.pur_tax_ids:
                    if tax_line.amount_type == 'percent':
                        total += tax_line.amount * hotel.supplier_price_total
                    else:
                        total += tax_line.amount
            for travel in obj.travel_planer_ids:
                for tax_line in travel.pur_tax_ids:
                    if tax_line.amount_type == 'percent':
                        total += tax_line.amount * (travel.price_total_adult + travel.price_total_child)
                    else:
                        total += tax_line.amount
            res[obj.id] = total
        return res
    
#     def _get_tax_amt_pur(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         total = 0.00
#         for obj in self.browse(cr, uid, ids):
#             for service in obj.service_ids:
#                 for tax_line in service.pur_tax_ids:
#                     if tax_line.amount_type == 'percent':
#                         total += tax_line.amount * service.price_subtotal_cost
#                     else:
#                         total += tax_line.amount
#             for site in obj.sites_costing_ids:
#                 for tax_line in site.pur_tax_ids:
#                     if tax_line.amount_type == 'percent':
#                         total += tax_line.amount * site.total_cost_price
#                     else:
#                         total += tax_line.amount
#             for visa in obj.visa_costing_ids:
#                 for tax_line in visa.pur_tax_ids:
#                     if tax_line.amount_type == 'percent':
#                         total += tax_line.amount * visa.total_cost_price
#                     else:
#                         total += tax_line.amount
#             for hotel in obj.hotel_planer_ids:
#                 for tax_line in hotel.pur_tax_ids:
#                     if tax_line.amount_type == 'percent':
#                         total += tax_line.amount * hotel.supplier_price_total
#                     else:
#                         total += tax_line.amount
#             for travel in obj.travel_planer_ids:
#                 for tax_line in travel.pur_tax_ids:
#                     if tax_line.amount_type == 'percent':
#                         total += tax_line.amount * (travel.price_total_adult + travel.price_total_child)
#                     else:
#                         total += tax_line.amount
#             res[obj.id] = total
#         return res 
    
    
    def _get_untax_amt_pur(self):
        res = {}
        total = 0.00
        for obj in self:
            for service in obj.service_ids:
                total += service.price_subtotal_cost
            for site in obj.sites_costing_ids:
                total += site.total_cost_price
            for visa in obj.visa_costing_ids:
                total += visa.total_cost_price
            for hotel in obj.hotel_planer_ids:
                total += hotel.supplier_price_total
            for travel in obj.travel_planer_ids:
                total += travel.price_total_adult + travel.price_total_child
            res[obj.id] = total
        return res
    
#     def _get_untax_amt_pur(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         total = 0.00
#         for obj in self.browse(cr,uid,ids):
#             for service in obj.service_ids:
#                 total += service.price_subtotal_cost
#             for site in obj.sites_costing_ids:
#                 total += site.total_cost_price
#             for visa in obj.visa_costing_ids:
#                 total += visa.total_cost_price
#             for hotel in obj.hotel_planer_ids:
#                 total += hotel.supplier_price_total
#             for travel in obj.travel_planer_ids:
#                 total += travel.price_total_adult + travel.price_total_child
#             res[obj.id] = total
#         return res 
    
    
    def _get_total_amt_sale(self):
        res = {}
        for obj in self:
            untax = obj._get_untax_amt_sale()
            tax_amt = obj._get_tax_amt_sale()
            res[obj.id] = untax[obj.id] + tax_amt[obj.id]
        return res
    
#     def _get_total_amt_sale(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         for obj in self.browse(cr, uid, ids):
#             untax = self._get_untax_amt_sale(cr, uid, [obj.id],args1,args2)
#             tax_amt = self._get_tax_amt_sale(cr, uid, [obj.id],args1,args2)
#             res[obj.id] = untax[obj.id] + tax_amt[obj.id]
#         return res
    
    
    def _get_tax_amt_sale(self):
        res = {}
        total = 0.00
        for obj in self:
            for service in obj.service_ids:
                for tax_line in service.sale_tax_ids:
                    if tax_line.amount_type == 'percent':
                        total += tax_line.amount * service.price_subtotal
                    else:
                        total += tax_line.amount
            for site in obj.sites_costing_ids:
                for tax_line in site.sale_tax_ids:
                    if tax_line.amount_type == 'percent':
                        total += tax_line.amount * site.total_sale_price
                    else:
                        total += tax_line.amount
            for visa in obj.visa_costing_ids:
                for tax_line in visa.sale_tax_ids:
                    if tax_line.amount_type == 'percent':
                        total += tax_line.amount * visa.total_sale_price
                    else:
                        total += tax_line.amount
            for hotel in obj.hotel_planer_ids:
                for tax_line in hotel.sale_tax_ids:
                    if tax_line.amount_type == 'percent':
                        total += tax_line.amount * hotel.customer_price_total
                    else:
                        total += tax_line.amount
            for travel in obj.travel_planer_ids:
                for tax_line in travel.sale_tax_ids:
                    if tax_line.amount_type == 'percent':
                        total += tax_line.amount * (travel.price_total_adult_sale + travel.price_total_child_sale)
                    else:
                        total += tax_line.amount
            res[obj.id] = total
        return res
    
#     def _get_tax_amt_sale(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         total = 0.00
#         for obj in self.browse(cr, uid, ids):
#             for service in obj.service_ids:
#                 for tax_line in service.sale_tax_ids:
#                     if tax_line.amount_type == 'percent':
#                         total += tax_line.amount * service.price_subtotal
#                     else:
#                         total += tax_line.amount
#             for site in obj.sites_costing_ids:
#                 for tax_line in site.sale_tax_ids:
#                     if tax_line.amount_type == 'percent':
#                         total += tax_line.amount * site.total_sale_price
#                     else:
#                         total += tax_line.amount
#             for visa in obj.visa_costing_ids:
#                 for tax_line in visa.sale_tax_ids:
#                     if tax_line.amount_type == 'percent':
#                         total += tax_line.amount * visa.total_sale_price
#                     else:
#                         total += tax_line.amount
#             for hotel in obj.hotel_planer_ids:
#                 for tax_line in hotel.sale_tax_ids:
#                     if tax_line.amount_type == 'percent':
#                         total += tax_line.amount * hotel.customer_price_total
#                     else:
#                         total += tax_line.amount
#             for travel in obj.travel_planer_ids:
#                 for tax_line in travel.sale_tax_ids:
#                     if tax_line.amount_type == 'percent':
#                         total += tax_line.amount * (travel.price_total_adult_sale + travel.price_total_child_sale)
#                     else:
#                         total += tax_line.amount
#             res[obj.id] = total
#         return res 
    
    
    def _get_untax_amt_sale(self):
        res = {}
        total = 0.00
        for obj in self:
            for service in obj.service_ids:
                total += service.price_subtotal
            for site in obj.sites_costing_ids:
                total += site.total_sale_price
            for visa in obj.visa_costing_ids:
                total += visa.total_sale_price
            for hotel in obj.hotel_planer_ids:
                total += hotel.customer_price_total
            for travel in obj.travel_planer_ids:
                total += travel.price_total_adult_sale + travel.price_total_child_sale
            res[obj.id] = total
        return res
    
#     def _get_untax_amt_sale(self,cr,uidif enq_browse.destination_lines_ids:
#             for destination in enq_browse.destination_lines_ids:
#                 print("ssssssssssssssssssssllllllllllll")
#                 destination_id = self.env['tour.destination.line'].create({
#                                                                            'destination_id': destination.destination_id.id,
#                                                                            'country_id': destination.country_id.id,
#                                                                            'name': destination.name,
#                                                                            'itinarary_id':so.id
#                                                                         }),ids,args1,args2,context=None):
# #         res = {}
#         total = 0.00
#         for obj in self.browse(cr,uid,ids):
#             for service in obj.service_ids:
#                 total += service.price_subtotal
#             for site in obj.sites_costing_ids:
#                 total += site.total_sale_price
#             for visa in obj.visa_costing_ids:
#                 total += visa.total_sale_price
#             for hotel in obj.hotel_planer_ids:
#                 total += hotel.customer_price_total
#             for travel in obj.travel_planer_ids:
#                 total += travel.price_total_adult_sale + travel.price_total_child_sale
#             res[obj.id] = total
#         return res 
      
    @api.multi
    @api.depends('total_seat', 'sites_costing_ids', 'visa_costing_ids', 'hotel_planer_ids', 'service_ids',
                 'travel_planer_ids', 'tour_program_ids', 'tour_destination_ids', 'itinary_cost_include_facility_lines',
                 'itinary_cost_exclude_facility_lines')
    def _get_adult_cost_price(self):
        print("hjjjjjjjjjjjjjjjj")
        res = {}
        total = 0.00
        for obj in self:
            for service in obj.service_ids:
                seat = 1
                if obj.total_seat:
                    seat = obj.total_seat
                total += ( service.price_subtotal / seat )
                for tax_line in service.sale_tax_ids:
                    if tax_line.amount_type == 'percent':
                        total += tax_line.amount/100 * ( service.price_subtotal / seat )
                    else:
                        total += tax_line.amount
            print("hjjjjjjjjjjjjjjjj",total)
            for site in obj.sites_costing_ids:
                total += site.sale_price
                for tax_line in site.sale_tax_ids:
                    if tax_line.amount_type == 'percent':
                        total += tax_line.amount/100 * site.sale_price
                    else:
                        total += tax_line.amount
            print("hjjjjjjjjjjjjjjjj1", total)
            for visa in obj.visa_costing_ids:
                total += visa.sale_price
                for tax_line in visa.sale_tax_ids:
                    if tax_line.amount_type == 'percent':
                        total += tax_line.amount/100     * visa.sale_price
                    else:
                        total += tax_line.amount

            print("hjjjjjjjjjjjjjjjj2", total)
            for hotel in obj.hotel_planer_ids:
                seat = 1
                if obj.total_seat:
                    seat = obj.total_seat
                total += (hotel.customer_price_total / seat)
                print("total-----------------",total)
                for tax_line in hotel.sale_tax_ids:
                    if tax_line.amount_type == 'percent':
                        total += (tax_line.amount)/100 * (hotel.customer_price_total / seat )
                        print("total-----------------", total,tax_line.amount,type(tax_line.amount))

                    else:
                        total += tax_line.amount
                        print("total-----------------", total)

            print("hjjjjjjjjjjjjjjjj3", total)
            for travel in obj.travel_planer_ids:
                total += travel.price_total_adult_sale
                print("tt-------------------",total,travel.price_total_adult_sale)
                for tax_line in travel.sale_tax_ids:
                    if tax_line.amount_type == 'percent':
                        total += tax_line.amount/100 * travel.price_total_adult_sale
                    else:
                        total += tax_line.amount
            print("hjjjjjjjjjjjjjjjj4", total)
            # res[obj.id] = round(total)
            # print("res[obj.id]--------------------",res[obj.id])
            self.adult_cost_price=total
        return res
    
#     def _get_adult_cost_price(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         total = 0.00
#         for obj in self.browse(cr,uid,ids):
#             for service in obj.service_ids:
#                 seat = 1
#                 if obj.total_seat:
#                     seat = obj.total_seat
#                 total += ( service.price_subtotal / seat )
#                 for tax_line in service.sale_tax_ids:
#                     if tax_line.amount_type == 'percent':
#                         total += tax_line.amount * ( service.price_subtotal / seat )
#                     else:
#                         total += tax_line.amount
#             for site in obj.sites_costing_ids:
#                 total += site.sale_price
#                 for tax_line in site.sale_tax_ids:
#                     if tax_line.amount_type == 'percent':
#                         total += tax_line.amount * site.sale_price
#                     else:
#                         total += tax_line.amount
#             for visa in obj.visa_costing_ids:
#                 total += visa.sale_price
#                 for tax_line in visa.sale_tax_ids:
#                     if tax_line.amount_type == 'percent':
#                         total += tax_line.amount * visa.sale_price
#                     else:
#                         total += tax_line.amount
#             for hotel in obj.hotel_planer_ids:
#                 seat = 1
#                 if obj.total_seat:
#                     seat = obj.total_seat
#                 total += (hotel.customer_price_total / seat)
#                 for tax_line in hotel.sale_tax_ids:
#                     if tax_line.amount_type == 'percent':
#                         total += tax_line.amount * (hotel.customer_price_total / seat )
#                     else:
#                         total += tax_line.amount
#             for travel in obj.travel_planer_ids:
#                 total += travel.sale_price
#                 for tax_line in travel.sale_tax_ids:
#                     if tax_line.amount_type == 'percent':
#                         total += tax_line.amount * travel.sale_price
#                     else:
#                         total += tax_line.amount
#             res[obj.id] = round(total)
#         return res 

    @api.multi
    @api.depends('total_seat', 'sites_costing_ids', 'visa_costing_ids', 'hotel_planer_ids', 'service_ids',
                 'travel_planer_ids','tour_program_ids','tour_destination_ids','itinary_cost_include_facility_lines','itinary_cost_exclude_facility_lines')
    def _get_child_cost_price(self):
        res = {}
        total = 0.00
        for obj in self:
            for service in obj.service_ids:
                seat = 1
                if obj.total_seat:
                    seat = obj.total_seat
                total += ( service.price_subtotal / seat )
                for tax_line in service.sale_tax_ids:
                    if tax_line.amount_type == 'percent':
                        total += tax_line.amount/100 * ( service.price_subtotal / seat )
                    else:
                        total += tax_line.amount
            for site in obj.sites_costing_ids:
                total += site.sale_price
                for tax_line in site.sale_tax_ids:
                    if tax_line.amount_type == 'percent':
                        total += tax_line.amount/100 * site.sale_price
                    else:
                        total += tax_line.amount
            for visa in obj.visa_costing_ids:
                total += visa.sale_price
                for tax_line in visa.sale_tax_ids:
                    if tax_line.amount_type == 'percent':
                        total += tax_line.amount/100 * visa.sale_price
                    else:
                        total += tax_line.amount
            for hotel in obj.hotel_planer_ids:
                seat = 1
                if obj.total_seat:
                    seat = obj.total_seat
                total += (hotel.customer_price_total / seat )
                for tax_line in hotel.sale_tax_ids:
                    if tax_line.amount_type == 'percent':
                        total += tax_line.amount/100 * (hotel.customer_price_total / seat )
                    else:
                        total += tax_line.amount
            for travel in obj.travel_planer_ids:
                total += travel.sale_price_child
                for tax_line in travel.sale_tax_ids:
                    if tax_line.amount_type == 'percent':
                        total += tax_line.amount/100 * travel.sale_price_child
                    else:
                        total += tax_line.amount
            self.child_cost_price=total
        return res
    
#     def _get_child_cost_price(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         total = 0.00
#         for obj in self.browse(cr,uid,ids):
#             for service in obj.service_ids:
#                 seat = 1
#                 if obj.total_seat:
#                     seat = obj.total_seat
#                 total += ( service.price_subtotal / seat )
#                 for tax_line in service.sale_tax_ids:
#                     if tax_line.amount_type == 'percent':
#                         total += tax_line.amount * ( service.price_subtotal / seat )
#                     else:
#                         total += tax_line.amount
#             for site in obj.sites_costing_ids:
#                 total += site.sale_price
#                 for tax_line in site.sale_tax_ids:
#                     if tax_line.amount_type == 'percent':
#                         total += tax_line.amount * site.sale_price
#                     else:
#                         total += tax_line.amount
#             for visa in obj.visa_costing_ids:
#                 total += visa.sale_price
#                 for tax_line in visa.sale_tax_ids:
#                     if tax_line.amount_type == 'percent':
#                         total += tax_line.amount * visa.sale_price
#                     else:
#                         total += tax_line.amount
#             for hotel in obj.hotel_planer_ids:
#                 seat = 1
#                 if obj.total_seat:
#                     seat = obj.total_seat
#                 total += (hotel.customer_price_total / seat )
#                 for tax_line in hotel.sale_tax_ids:
#                     if tax_line.amount_type == 'percent':
#                         total += tax_line.amount * (hotel.customer_price_total / seat )
#                     else:
#                         total += tax_line.amount
#             for travel in obj.travel_planer_ids:
#                 total += travel.sale_price_child
#                 for tax_line in travel.sale_tax_ids:
#                     if tax_line.amount_type == 'percent':
#                         total += tax_line.amount * travel.sale_price_child
#                     else:
#                         total += tax_line.amount
#             res[obj.id] = round(total)
#         return res 
      
    
    
    name = fields.Char("Itinerary No.",size=128,readonly=True)
    tour_pref_id = fields.Many2one('tour.preference','Customer Enquiry No',required=True,readonly=True, states={'draft': [('readonly', False)]},)
    current_date = fields.Date("Enquiry Date",required=True,readonly=True, states={'draft': [('readonly', False)]},default=lambda *args: time.strftime('%Y-%m-%d'))
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', required=True,readonly=True, states={'draft':[('readonly',False)]})
    lead = fields.Many2one('crm.lead','Lead',required=True)
    contact_name = fields.Char('Contact Name',size=64,readonly=True, states={'draft': [('readonly', False)]},)
    address = fields.Char('Address',size=256,readonly=True, states={'draft': [('readonly', False)]},)
    email_id = fields.Char('Email Id',size=64,readonly=True, states={'draft': [('readonly', False)]},)
    tour_name = fields.Many2one('tour.package','Tour name',required=True)
    mobile = fields.Char('Mobile Number',size=15, required=True,readonly=True, states={'draft': [('readonly', False)]},)
    adult = fields.Integer("Adult Persons",readonly=True, states={'draft': [('readonly', False)]},)
    child = fields.Integer("Child",readonly=True, states={'draft': [('readonly', False)]},)
    room_req = fields.Integer("Room Required",readonly=True, states={'draft': [('readonly', False)]},)
    checkin_date = fields.Date("Prefer start Date",required=True,readonly=True, states={'draft': [('readonly', False)]})
    checkout_date = fields.Date("Prefer End Date",required=True,readonly=True, states={'draft': [('readonly', False)]},)
    country_id = fields.Many2one('res.country','Origin',required=True,readonly=True, states={'draft': [('readonly', False)]},)
    via = fields.Selection([('direct','Direct'),('agent','Agent')],string="Via",readonly=True, states={'draft': [('readonly', False)]},default=lambda * a: 'direct')
    agent_id = fields.Many2one('res.partner','Agent',readonly=True, states={'draft': [('readonly', False)]},)
    hotel_planer_ids = fields.One2many('hotel.planer.details','hotel_planer_id','Hotel Planer',readonly=True, states={'draft': [('readonly', False)]},)
    travel_planer_ids = fields.One2many('travel.planer.details','travel_planer_id','Travel Planer',readonly=True, states={'draft': [('readonly', False)]},)
    tour_program_ids = fields.One2many('custom.tour.programme','program_id','Tour Program',readonly=True, states={'draft': [('readonly', False)]},)
    tour_destination_ids = fields.One2many('tour.destination.line','itinarary_id','Tour Destination Lines',readonly=True, states={'draft': [('readonly', False)]},)
    state = fields.Selection([
                               ('draft', 'Draft'),
                               ('confirm', 'Confirm'),
                               ('send_to', 'Sent To Customer'),
                               ('approve', 'Approved'),
                               ('refused', 'Refused'),
                               ('done', 'Done'),
                               ], string='Status',default=lambda * a: 'draft')
    start_date = fields.Date("Start Date",required=True,readonly=True, states={'draft': [('readonly', False)]},)
    book_date = fields.Date("Last Date of Booking",required=True,readonly=True, states={'draft': [('readonly', False)]},)
    due_date = fields.Date("Payment Due Date",required=True,readonly=True, states={'draft': [('readonly', False)]},)
    total_seat = fields.Integer(compute=_get_total_seat,string="Total Seats", store=True)
    adult_cost_price = fields.Float(compute=_get_adult_cost_price, string="Sale Price/ Person(Adult)", store=True)
    child_cost_price = fields.Float(compute=_get_child_cost_price, string="Sale Price/ Person(Child)", store=True)
    itinary_cost_include_facility_lines = fields.One2many('tour.cost.include.facility','itinary_id','Tour Cost Included Facility Lines',readonly=True, states={'draft': [('readonly', False)]})
    itinary_cost_exclude_facility_lines = fields.One2many('tour.cost.exclude.facility','itinary_id','Tour Cost Excluded Facility Lines',readonly=True, states={'draft': [('readonly', False)]})
    sites_costing_ids = fields.One2many('sites.costing.line','itinary_id','Sites Costing')
    visa_costing_ids = fields.One2many('visa.costing.line','itinary_id','Sites Costing',readonly=True)
    service_ids = fields.One2many('tour.service.line.details','itinarary_id','Other Services')
    sale_untax_amt = fields.Float(compute=_get_untax_amt_sale, string="Sale Untaxed Amount", store=True)
    sale_tax_amt = fields.Float(compute=_get_tax_amt_sale,string="Sale Taxes ", store=True)
    pur_untax_amt = fields.Float(compute=_get_untax_amt_pur, string="Purchase Untaxed Amount", store=True)
    pur_tax_amt = fields.Float(compute=_get_tax_amt_pur,string="Purchase Taxes ", store=True)
    sale_total_amt = fields.Float(compute=_get_total_amt_sale, string="Sale Total Amount", store=True)
    pur_total_amt = fields.Float(compute=_get_total_amt_pur, string="Purchase Total Amount", store=True)
    payment_policy_id = fields.Many2one('tour.payment.policy',string="Payment Policy",required=True,readonly=True, states={'draft': [('readonly', False)]},)
    
    
#     _defaults = {
#                  'state': lambda * a: 'draft',
#                  'via': lambda * a: 'direct',
#                  'current_date':lambda *args: time.strftime('%Y-%m-%d'),
#                  }
    
    _sql_constraints = [
        ('checkin_checkout_date12', 'CHECK (checkout_date > checkin_date)',  "Preferred end date must be greater than Preferred start date !"),
    ]
    
    
    @api.onchange('tour_pref_id')
    def on_change_tour_pref_id(self):
        result = {}
        if self.tour_pref_id:
            obj = self.tour_pref_id
            result['lead'] = obj.lead.id
            result['address'] = obj.address
            result['contact_name'] = obj.contact_name
            result['email_id'] = obj.email_id
            result['mobile'] = obj.mobile
            result['adult'] = obj.adult
            result['child'] = obj.child
            result['country_id'] = obj.country_id.id
            result['room_req'] = obj.room_req
            result['checkin_date'] = obj.checkin_date
            result['checkout_date'] = obj.checkout_date
            result['via'] = obj.via
            result['agent_id'] = obj.agent_id.id
            result['total_seat'] = (obj.adult + obj.child)
            

            # tour_destination_ids=[]
            # for record in obj.destination_lines_ids:
            #     tour_destination_ids.append((0,0,{
            #         'destination_id': record.destination_id.id,
            #         'country_id': record.country_id.id,
            #         'name': record.name
            #         }))
            #     print (tour_destination_ids)
            # result['tour_destination_ids']=tour_destination_ids
                
        
#         if self._ids and self.tour_pref_id:
#             obj_itinaray = self[0]
#             if obj_itinaray.tour_destination_ids:
#                 for dest in obj_itinaray.tour_destination_ids:
#                     dest.unlink()
#             if self.tour_pref_id.destination_lines_ids:
#                 for destination in obj.destination_lines_ids:
#                     destination_id = self.env['tour.destination.line'].create({
#                                                                                'destination_id': destination.destination_id.id,
#                                                                                'country_id': destination.country_id.id,
#                                                                                'name': destination.name,
#                                                                                'itinarary_id':self.id
#                                                                             })
        return {'value': result}
    
    @api.onchange('tour_name')
    def on_change_tour_name(self):
        if self.tour_name and self.tour_name.tour_date_lines:
            obj = self.tour_name
            self.start_date=obj.tour_date_lines[0].start_date
            self.book_date=obj.tour_date_lines[0].book_date
            self.due_date=obj.tour_date_lines[0].due_date
            
            # tour_destination_ids=[]
            # for record in obj.tour_destination_lines:
            #     tour_destination_ids.append((0,0,{
            #         'destination_id': record.destination_id.id,
            #         'country_id': record.country_id.id,
            #         'name': record.name
            #         }))
            #
            # self.tour_destination_ids=tour_destination_ids
    
    
    
#     def on_change_tour_pref_id(self,cr,uid,ids,tour_pref_id):
#         result = {}
#         if tour_pref_id:
#             obj = self.pool.get('tour.preference').browse(cr,uid,tour_pref_id)
#             print obj.lead,"obj.lead"
#             result['lead'] = obj.lead.id
#             result['address'] = obj.address
#             result['contact_name'] = obj.contact_name
#             result['email_id'] = obj.email_id
#             result['mobile'] = obj.mobile
#             result['adult'] = obj.adult
#             result['child'] = obj.child
#             result['country_id'] = obj.country_id.id
#             result['room_req'] = obj.room_req
#             result['checkin_date'] = obj.checkin_date
#             result['checkout_date'] = obj.checkout_date
#             result['via'] = obj.via
#             result['agent_id'] = obj.agent_id.id
#             result['total_seat'] = (obj.adult + obj.child)
#         if ids and tour_pref_id:
#             obj_itinaray = self.browse(cr,uid,ids)[0]
#             if obj_itinaray.tour_destination_ids:
#                 for dest in obj_itinaray.tour_destination_ids:
#                     self.pool.get('tour.destination.line').unlink(cr,uid,dest.id)
#             obj = self.pool.get('tour.preference').browse(cr,uid,tour_pref_id)
#             if obj.destination_lines_ids:
#                 for destination in obj.destination_lines_ids:
#                     print destination
#                     destination_id = self.pool.get('tour.destination.line').create(cr, uid, {
#                                                                                            'destination_id': destination.destination_id.id,
#                                                                                            'country_id': destination.country_id.id,
#                                                                                            'name': destination.name,
#                                                                                            'itinarary_id':ids[0]
#                                                                                            })
#         return {'value': result}
    
    
    @api.onchange('lead')
    def on_change_lead_id(self):
        result = {}
        if self.lead:
            res = self.lead
            address = ''
            if res.street:
                address += res.street + ' '
            if res.street2:
                address += res.street2 + ' '
            if res.city:
                address += res.city  + ' '
            if res.zip:
                address += res.zip + ' '
            result['address'] = address
            result['contact_name'] = res.contact_name
            result['mobile'] = res.mobile
            result['email_id'] = res.email_from   
            result['country_id'] = res.country_id.id
            result['via'] = res.via
            result['agent_id'] = res.agent_id.id
        return result
    
#     def on_change_lead_id(self,cr,uid,ids,lead_id):
#         result = {}
#         if lead_id:
#             res = self.pool.get('crm.lead').browse(cr,uid,lead_id)
#             address = ''
#             if res.street:
#                 address += res.street + ' '
#             if res.street2:
#                 address += res.street2 + ' '
#             if res.city:
#                 address += res.city  + ' '
#             if res.zip:
#                 address += res.zip + ' '
#             result['address'] = address
#             result['contact_name'] = res.contact_name
#             result['mobile'] = res.mobile
#             result['email_id'] = res.email_from   
#             result['country_id'] = res.country_id.id
#             result['via'] = res.via
#             result['agent_id'] = res.agent_id.id
#             pr/home/pravin/Documents/odoo-12.0.post20190408/tour_addons/custom_tour_operation/models/custom_tour_operation.pyint "result",result
#         return result
    
    
    
    @api.depends('hotel_planer_ids', 'sites_costing_ids', 'visa_costing_ids', 'service_ids', 'travel_planer_ids')
    @api.onchange('pricelist_id')
    def onchange_pricelist_id(self):
        if (not self.pricelist_id) or ((not self.hotel_planer_ids) and (not self.sites_costing_ids) and (not self.visa_costing_ids) and (not self.service_ids) and (not self.travel_planer_ids)):
            return {}
        warning = {
            'title': _('Pricelist Warning!'),
            'message' : _('If you change the pricelist of this order (and eventually the currency), prices of existing order lines will not be updated.')
        }
        return {'warning': warning}
    
#     def onchange_pricelist_id(self, cr, uid, ids, pricelist_id, hotel_planer_ids, sites_costing_ids, visa_costing_ids, service_ids, travel_planer_ids, context={}):
#         if (not pricelist_id) or ((not hotel_planer_ids) and (not sites_costing_ids) and (not visa_costing_ids) and (not service_ids) and (not travel_planer_ids)):
#             return {}
#         warning = {
#             'title': _('Pricelist Warning!'),
#             'message' : _('If you change the pricelist of this order (and eventually the currency), prices of existing order lines will not be updated.')
#         }
#         return {'warning': warning}
    
    
    @api.onchange("adult",'child')
    def on_change_adult_child(self):
        result = {}
        total = 0
        if self.adult:
            total += self.adult
        if self.child:
            total += self.child
        result['total_seat'] = total
        return {'value': result}
    
#     def on_change_adult_child(self,cr,uid,ids,adult,child):
#         result = {}
#         total = 0
#         if adult:
#             total += adult
#         if child:
#             total += child
#         result['total_seat'] = total
#         print "result",result
#         return {'value': result}
    
    
    @api.multi
    def action_confirm(self):
        for obj in self:
            if (obj.due_date < obj.book_date):
                raise UserError('Payment Due Date should not be less than Last Date of Booking.')
            if (obj.due_date > obj.start_date):
                raise UserError('Payment Due Date should not be greater than Tour Start Date.')
        self.write({'state':'confirm'})
        return True
    
#     def action_confirm(self, cr, uid, ids, *args):
#         for obj in self.browse(cr,uid,ids):
#             if (obj.due_date < obj.book_date):
#                 raise osv.except_osv(_('Error !'), _('Payment Due Date should not be less than Last Date of Booking.'))
#             if (obj.due_date > obj.start_date):
#                 raise osv.except_osv(_('Error !'), _('Payment Due Date should not be greater than Tour Start Date.'))
#         self.write(cr, uid, ids, {'state':'confirm'})
#         return True
    
#        This method update be maulik
    
    
    @api.multi
    def action_approve(self):
        for obj in self:
            id_lead = obj.lead
            data_obj = self.env['ir.model.data']
            data_id = data_obj._get_id('crm', 'view_crm_lead2opportunity_partner')
            view_id1 = False
            if self._context is None:
                self._context = {}
            ctx = self._context.copy()
            ctx['active_ids'] = [id_lead.id]
            ctx['banquet_id'] = obj.id
            if data_id:
                view_id1 = data_obj.res_id

            opp = {
                    'name': _('Create Partner'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'crm.lead2opportunity.partner',
                    'view_id': False,
                    'context': ctx,
                    'views': [(view_id1, 'form')],
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'nodestroy': True
                    }
            rejected_history_id = self.env['itinerary.lead.history'].search([('ref_id', '=', id_lead.id)])
            if rejected_history_id:
                for id in rejected_history_id:
                    self.env['itinerary.lead.history'].write({'state':'refused','update_date':time.strftime('%Y-%m-%d')})
            history_id = self.env['itinerary.lead.history'].search([('name', '=', obj.name),('ref_id', '=', id_lead.id)])
            if history_id:
                history_id.write({'state':'approve','update_date':time.strftime('%Y-%m-%d')})
           
            rejected_itinary = self.search([('tour_pref_id', '=', obj.tour_pref_id.id)])
            if rejected_itinary:
                for id in rejected_itinary:
                    id.write({'state':'refused'})
            obj.tour_pref_id.write({'state':'confirm'})

        self.write({'state':'approve'})
        return opp
    
#     def action_approve(self, cr, uid, ids,context=None, *args):
#         for obj in self.browse(cr,uid,ids):
#             id_lead = self.pool.get('crm.lead').browse(cr,uid,obj.lead.id)
#             data_obj = self.pool.get('ir.model.data')
#             data_id = data_obj._get_id(cr, uid, 'crm', 'view_crm_lead2opportunity_partner')
#             print data_id,"data_id=------------------------"
#             view_id1 = False
#             if context is None:
#                 context = {}
#             context['active_ids'] = [id_lead.id]
#             context['banquet_id'] = obj.id
#             if data_id:
#                 view_id1 = data_obj.browse(cr, uid, data_id, context).res_id
#             opp = {
#                     'name': _('Create Partner'),
#                     'view_type': 'form',
#                     'view_mode': 'form',
#                     'res_model': 'crm.lead2opportunity.partner',
#                     'view_id': False,
#                     'context': context,
#                     'views': [(view_id1, 'form')],
#                     'type': 'ir.actions.act_window',
#                     'target': 'new',
#                     'nodestroy': True
#                     }
#             rejected_history_id = self.pool.get('itinerary.lead.history').search(cr, uid, [('ref_id', '=', id_lead.id)])
#             if rejected_history_id:
#                 for id in rejected_history_id:
#                     self.pool.get('itinerary.lead.history').write(cr, uid, id, {'state':'refused','update_date':time.strftime('%Y-%m-%d')})
#             history_id = self.pool.get('itinerary.lead.history').search(cr, uid, [('name', '=', obj.name),('ref_id', '=', id_lead.id)])
#             print history_id,"history_id=============="
#             if history_id:
#                 self.pool.get('itinerary.lead.history').write(cr, uid, history_id, {'state':'approve','update_date':time.strftime('%Y-%m-%d')})
#                 print history_id,"history_id"
#            
#             rejected_itinary = self.search(cr, uid, [('tour_pref_id', '=', obj.tour_pref_id.id)])
#             if rejected_itinary:
#                 for id in rejected_itinary:
#                     self.write(cr, uid, id, {'state':'refused'})
#             self.pool.get('tour.preference').write(cr, uid, obj.tour_pref_id.id, {'state':'confirm'})
#         self.write(cr, uid, ids, {'state':'approve'})
#         return opp
    
    
    @api.multi
    def action_refuse(self):
        for obj in self:
            id_lead = obj.lead
            history_id = self.env['itinerary.lead.history'].search([('name', '=', obj.name),('ref_id', '=', id_lead.id)])
            if history_id:
                history_id.write({'state':'refused','update_date':time.strftime('%Y-%m-%d')})
        self.write({'state':'refused'})
        return True
    
#     def action_refuse(self, cr, uid, ids, *args):
#         for obj in self.browse(cr,uid,ids):
#             id_lead = self.pool.get('crm.lead').browse(cr,uid,obj.lead.id)
#             history_id = self.pool.get('itinerary.lead.history').search(cr, uid, [('name', '=', obj.name),('ref_id', '=', id_lead.id)])
#             print history_id,"history_id=============="
#             if history_id:
#                 self.pool.get('itinerary.lead.history').write(cr, uid, history_id, {'state':'refused','update_date':time.strftime('%Y-%m-%d')})
#                 print history_id,"history_id"
#         self.write(cr, uid, ids, {'state':'refused'})
#         return True
    
    
    @api.multi
    def action_sent(self):
        for obj in self:
            id_lead = obj.lead
            itinarary_id = self.env['itinerary.lead.history'].create({
                                                                                   'name': obj.name,
                                                                                   'contact_name':obj.contact_name,
                                                                                   'state':'send_to',
                                                                                   'ref_id':id_lead.id,
                                                                                   'current_date': time.strftime('%Y-%m-%d'),
                                                                                   'update_date': time.strftime('%Y-%m-%d'),
                                                                                   })
            stage = self.env['crm.stage'].search([('name', '=', 'Proposition')])
            if stage:
                user_id = self.env['res.users'].browse(self._uid)
                details = user_id.name + ' on' + time.strftime('%Y-%m-%d %H:%M:%S') + ' : changes Stage to : Proposition'
                data = {
                        'name': 'Stage',
                        'history': True,
                        'user_id': self._uid,
                        'model' : 'crm.lead',
                        'res_id': id_lead.id,
                        'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'description': details,
                    }
                self._cr.execute('update crm_lead set stage_id=%s where id=%s', (stage[0].id, id_lead.id))
        self.write({'state':'send_to'})
        return True
    
#     def action_sent(self, cr, uid, ids, *args):
#         for obj in self.browse(cr,uid,ids):
#             id_lead = self.pool.get('crm.lead').browse(cr,uid,obj.lead.id)
#             print id_lead,"id_lead"
#             itinarary_id = self.pool.get('itinerary.lead.history').create(cr, uid, {
#                                                                                    'name': obj.name,
#                                                                                    'contact_name':obj.contact_name,
#                                                                                    'state':'send_to',
#                                                                                    'ref_id':id_lead.id,
#                                                                                    'current_date': time.strftime('%Y-%m-%d'),
#                                                                                    'update_date': time.strftime('%Y-%m-%d'),
#                                                                                    })
#             stage = self.pool.get('crm.stage').search(cr, uid, [('name', '=', 'Proposition')])
#             if stage:
#                 mail_gate = self.pool.get('mailgate.message')
#                 user_id = self.pool.get('res.users').browse(cr,uid,uid)
#                 details = user_id.name + ' on' + time.strftime('%Y-%m-%d %H:%M:%S') + ' : changes Stage to : Proposition'
#                 data = {
#                         'name': 'Stage',
#                         'history': True,
#                         'user_id': uid,
#                         'model' : 'crm.lead',
#                         'res_id': id_lead.id,
#                         'date': time.strftime('%Y-%m-%d %H:%M:%S'),
#                         'description': details,
#                     }
#                 cr.execute('update crm_lead set stage_id=%s where id=%s', (stage[0], id_lead.id))
#         self.write(cr, uid, ids, {'state':'send_to'})
#         return True
    
    @api.multi
    def action_create_tour(self):
        for obj in self:
            id_lead = obj.lead
            self._cr.execute("""select id from product_template where name='Custom Tour'""")                        
            p_id = self._cr.fetchone()
            if not p_id:
                raise Warning('Please Configuration Custom Tour as a product.')
            if not id_lead.partner_id:
                raise Warning("Please convert the Lead '%s' in Opportunity first!" % (obj.lead.lead_sequence))
            product_id = p_id[0]
            country_flag = False
            for desti in obj.tour_destination_ids:
                if desti.country_id.id != obj.country_id.id:
                    country_flag = True
                    break
            if country_flag == True:
                tour_type = 'international'
            else:
                tour_type = 'domestic'
            tour_category = 'custom'
            dt_from = datetime.strptime(str(obj.checkin_date), '%Y-%m-%d')
            dt_to = datetime.strptime(str(obj.checkout_date), '%Y-%m-%d')
            no_of_days = int((dt_to - dt_from).days)
            if not obj.tour_name:
                tour_id = self.env['tour.package'].create({
                                                           'name1':obj.tour_name,
                                                           'product_id': obj.tour_name,
                                                           'tour_type':tour_type,
                                                           'current_date':time.strftime('%Y-%m-%d'),
                                                           'days':str(no_of_days),
                                                           'itinary_id':obj.id,
                                                           'tour_category':tour_category,
                                                           })
            else:
                obj.tour_name.write({
                                               'product_id': product_id,
                                               'tour_type':tour_type,
                                               'current_date':time.strftime('%Y-%m-%d'),
                                               'days':str(no_of_days),
                                               'itinary_id':obj.id,
                                               'tour_category':tour_category,
                                                           })
                tour_id = obj.tour_name


            print("tour_id--------------------------",tour_id)
            fmt = '%Y-%m-%d'
            t_date = datetime.strptime(str(obj.start_date), fmt)
            month_list = ("", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
            x = str(t_date.day) + '-' + month_list[t_date.month] + '-' + str(t_date.year)
            str_name = x
            season_id = self.env['ir.model.data'].get_object_reference('tour_travel', 'list14')[1]
            tour_dates_id = self.env['tour.dates'].create({
                                                           'name':str_name,
                                                           'season_id': season_id,
                                                           'start_date':obj.start_date,
                                                           'book_date':obj.book_date,
                                                           'due_date':obj.due_date,
                                                           'total_seat': obj.total_seat,
                                                           'available_seat':obj.total_seat,
                                                           'adult_cost_price':obj.adult_cost_price,
                                                           'child_cost_price':obj.child_cost_price,
                                                           'tour_id':tour_id.id,
                                                           'state':'available'
                                                           })
            print("tour_dates_id--------------------",tour_dates_id)
            for program in obj.tour_program_ids:
                tour_program_id = self.env['tour.programme'].create({
                                                                       'name':program.name.name,
                                                                       'description':program.description,
                                                                       'breakfast':program.breakfast,
                                                                       'lunch':program.lunch,
                                                                       'dinner': program.dinner,
                                                                       'tour_id1':tour_id.id,
                                                                       })

            # for program in obj.hotel_planer_ids:
            #     search_id = self.env['hotel.information'].search(
            #         [('hotel_id', '=', program.hotel_id.id), ('state', '=', 'confirm')], limit=1)
            #     hotel_planer_id=self.env['tour.destination.hotel.line'].create({
            #                                         'hotel_id':program.hotel_id.id,
            #                                         'hotel_type_id':program.hotel_type_id.id,
            #                                         'room_type_id':program.room_type_id.id,
            #                                         'tour_id': tour_id.id,
            #         })
            #     print("hotel_planer_id------------",hotel_planer_id)
            travel_planer_id=False
            for program0 in obj.travel_planer_ids:
                travel_planer_id = self.env['tour.road.travel'].create({
                    'from_destination_id': program0.from_destination_id.id,
                    'to_destination_id': program0.to_destination_id.id ,
                    'transport_type_id': program0.transport_type_id.id,
                    'travel_class_id':program0.travel_class_id.id,
                    'name':0.0,
                    'approx_time':0.0,

                    'tour_id': tour_id.id,
                })

                if travel_planer_id:

                    provider_information_id = self.env['provider.information.line'].create({
                        'provider_id': program0.transport_id.id,
                        'transport_carrier_id': program0.transport_carrier_id.id,
                        'name':True,
                        # 'tour_id': tour_id.id,
                        'ref_id1':travel_planer_id.id
                }

                )
                print("travel_planer_id----------------------",travel_planer_id)

            for program in obj.itinary_cost_include_facility_lines:
                program.write({'tour_id':tour_id.id})
            for program in obj.itinary_cost_exclude_facility_lines:
                program.write({'tour_id':tour_id.id})
            for program1 in obj.tour_destination_ids:
                program1.write({'tour_id':tour_id.id})


                for program in obj.hotel_planer_ids:
                    search_id = self.env['hotel.information'].search(
                        [('hotel_id', '=', program.hotel_id.id), ('state', '=', 'confirm')], limit=1)
                    hotel_planer_id=self.env['tour.destination.hotel.line'].create({
                                                        'hotel_id':program.hotel_id.id,
                                                        'hotel_type_id':program.hotel_type_id.id,
                                                        'room_type_id':program.room_type_id.id,
                                                        'tour_id': tour_id.id,
                                                        'destination_line_id':program1.id
                        })
                    print("hotel_planer_id------------",hotel_planer_id)
            # for program in obj.travel_planer_ids:
            #     program.write({'tour_id': tour_id.id})
            # for program in obj.hotel_planer_ids:
            #     program.write({'tour_id': tour_id.id})


            
            tour_booking = self.env['tour.booking'].create({
                                                           'current_date': time.strftime('%Y-%m-%d'),
                                                           'customer_id':id_lead.partner_id.id,
                                                           'email_id':obj.email_id,
                                                           'mobile1':obj.mobile,
                                                           'adult': obj.adult,
                                                           'child':obj.child,
                                                           'tour_type':tour_type,
                                                           'via':obj.via,
                                                           'agent_id':obj.agent_id.id,
                                                           'season_id':season_id,
                                                           'tour_id':tour_id.id,
                                                           'itinary_id':obj.id,
                                                           'tour_dates_id':tour_dates_id.id,
                                                           'pricelist_id':obj.pricelist_id.id,
                                                           'payment_policy_id':obj.payment_policy_id.id,
                                                           'state':'draft',
                                                           })
            print("tour_booking----------------------------------",tour_booking)
        self.write({'state':'done'})
        return True
    
#     def action_create_tour(self, cr, uid, ids, *args):
#         for obj in self.browse(cr,uid,ids):
#             print obj,"obj"
#             id_lead = self.pool.get('crm.lead').browse(cr,uid,obj.lead.id)
#             print id_lead,"id_lead"
#             cr.execute("""select id from product_template where name='Custom Tour'""")                        
#             p_id = cr.fetchone()
#             if not p_id:
#                 raise osv.except_osv(_('Configuration Error !'), _('Please Configuration Custom Tour as a product.'))
#             if not id_lead.partner_id:
#                 raise osv.except_osv(_("Warning"),_("Please convert the Lead '%s' in Opportunity first!") % (obj.lead.lead_sequence))
#             product_id = p_id[0]
#             print "Product",product_id
#             country_flag = False
#             for desti in obj.tour_destination_ids:
#                 if desti.country_id.id != obj.country_id.id:
#                     country_flag = True
#                     break
#             if country_flag == True:
#                 tour_type = 'international'
#             else:
#                 tour_type = 'domestic'
#             print tour_type,"tour_type"
#             tour_category = 'custom'
#             dt_from = mx.DateTime.strptime(obj.checkin_date, '%Y-%m-%d')
#             dt_to = mx.DateTime.strptime(obj.checkout_date, '%Y-%m-%d')
#             no_of_days = int((dt_to - dt_from).days)
#             tour_id = self.pool.get('tour.package').create(cr, uid, {
#                                                                    'name1':obj.tour_name,
#                                                                    'product_id': product_id,
#                                                                    'tour_type':tour_type,
#                                                                    'current_date':time.strftime('%Y-%m-%d'),
#                                                                    'days':str(no_of_days),
#                                                                    'itinary_id':obj.id,
#                                                                    'tour_category':tour_category,
#                                                                    })
#             print tour_id,"tour_id"
#             fmt = '%Y-%m-%d'
#             t_date = datetime.strptime(obj.start_date, fmt)
#             month_list = ("", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
#             x = str(t_date.day) + '-' + month_list[t_date.month] + '-' + str(t_date.year)
#             str_name = x 
#             tour_dates_id = self.pool.get('tour.dates').create(cr, uid, {
#                                                                        'name':str_name,
#                                                                        'season_id': 4,
#                                                                        'start_date':obj.start_date,
#                                                                        'book_date':obj.book_date,
#                                                                        'due_date':obj.due_date,
#                                                                        'total_seat': obj.total_seat,
#                                                                        'available_seat':obj.total_seat,
#                                                                        'adult_cost_price':obj.adult_cost_price,
#                                                                        'child_cost_price':obj.child_cost_price,
#                                                                        'tour_id':tour_id,
#                                                                        'state':'available'
#                                                                        })
#             print tour_dates_id,"tour_dates_id"
#             for program in obj.tour_program_ids:
#                 tour_program_id = self.pool.get('tour.programme').create(cr, uid, {
#                                                                            'name':program.name.name,
#                                                                            'description':program.description,
#                                                                            'breakfast':program.breakfast,
#                                                                            'lunch':program.lunch,
#                                                                            'dinner': program.dinner,
#                                                                            'tour_id1':tour_id,
#                                                                            })
#                 print tour_program_id,"tour_program_id"
#             for program in obj.itinary_cost_include_facility_lines:
#                 self.pool.get('tour.cost.include.facility').write(cr, uid, program.id, {'tour_id':tour_id})
#             for program in obj.itinary_cost_exclude_facility_lines:
#                 self.pool.get('tour.cost.exclude.facility').write(cr, uid, program.id, {'tour_id':tour_id})
#             for program in obj.tour_destination_ids:
#                 print program,"program"
#                 self.pool.get('tour.destination.line').write(cr, uid, [program.id], {'tour_id':tour_id})
#             tour_booking = self.pool.get('tour.booking').create(cr, uid, {
#                                                                        'current_date': time.strftime('%Y-%m-%d'),
#                                                                        'customer_id':id_lead.partner_id.id,
#                                                                        'email_id':obj.email_id,
#                                                                        'mobile1':obj.mobile,
#                                                                        'adult': obj.adult,
#                                                                        'child':obj.child,
#                                                                        'tour_type':tour_type,
#                                                                        'via':obj.via,
#                                                                        'agent_id':obj.agent_id.id,
#                                                                        'season_id':4,
#                                                                        'tour_id':tour_id,
#                                                                        'itinary_id':obj.id,
#                                                                        'tour_dates_id':tour_dates_id,
#                                                                        'pricelist_id':obj.pricelist_id.id,
#                                                                        'payment_policy_id':obj.payment_policy_id.id,
#                                                                        'state':'draft',
#                                                                        })
#             tour_search = self.pool.get('tour.booking').search(cr, uid, [('tour_id', '=', tour_id)])
#             custom_tour = self.pool.get('tour.booking').browse(cr,uid,tour_search)
#             print custom_tour[0].id,"custom_tour"
#             print tour_booking,"tour_booking",custom_tour[0].name
#         self.write(cr, uid, ids, {'state':'done'})
#         return True
    
    
    def compute(self):
        return True
    
#     def compute(self, cr, uid, ids, context=None):
#         return True
    


class tour_package(models.Model):
    _inherit = "tour.package"
    _description = "Tour Package"
    
    
    itinary_id = fields.Many2one('custom.tour.itinarary','Itinerary Id',readonly=True)




class tour_customer_details(models.Model):
    _inherit = "tour.customer.details"
    _description = "Tour Customer Details "
    
    
    @api.model
    def create(self,vals):
        """
        To override create method
        """
        if 'tour_book_id' in vals:
            if vals.get('tour_book_id'):
                visa = False
                hotel = False
                transport = False
                obj = self.env['tour.booking'].browse(vals['tour_book_id'])
                so = super(tour_customer_details, self).create(vals)
                if not obj.itinary_id:
                    return so
                else:
                    for visa_line in obj.tour_id.tour_destination_lines:
                        if visa_line.is_visa == True:
                            visa = True
                            break
                    if obj.itinary_id.hotel_planer_ids:

                        hotel = True
                    if obj.itinary_id.travel_planer_ids:
                        transport = True
                    vals.update({'v_flag': visa, 'h_flag':hotel, 't_flag':transport, })
                    so.write(vals)
        else:
            return super(tour_customer_details, self).create(vals)
        return so
    
#     def create(self, cr, uid, vals,context=None):
#         """
#         To override create method
#         """
#         print vals,"valsssssssssssss"
#         if vals.__contains__('tour_book_id'):
#             if vals['tour_book_id']:
#                 visa = False
#                 hotel = False
#                 transport = False
#                 obj = self.pool.get('tour.booking').browse(cr, uid, vals['tour_book_id'])
#                 so = super(tour_customer_details, self).create(cr, uid, vals,context=context)
#                 if not obj.itinary_id:
#                     return so
#                 else:
#                     for visa_line in obj.tour_id.tour_destination_lines:
#                         if visa_line.is_visa == True:
#                             visa = True
#                             break
#                     if obj.itinary_id.hotel_planer_ids:
#                         hotel = True
#                     if obj.itinary_id.travel_planer_ids:
#                         transport = True
#                     vals.update({'v_flag': visa, 'h_flag':hotel, 't_flag':transport, })
#                     self.write(cr, uid, so, vals)
#         else:
#             return super(tour_customer_details, self).create(cr, uid, vals,context=context)
#         return True
    



class tour_booking(models.Model):
    _inherit = "tour.booking"
    _description = "Tour Booking"
    
    itinary_id = fields.Many2one('custom.tour.itinarary','Itinerary Id',readonly=False)

    
    # @api.model
    # def create(self,vals):
    #     # function overwrites create method and auto generate request no.
    #     so = super(tour_booking, self).create(vals)
    #     if not vals['itinary_id'] and 'itinary_id' in vals:
    #         return so
    #     else:
    #         req_no = self.env['ir.sequence'].get('custom.tour.booking')
    #         vals['name'] = req_no
    #         vals.update({'name': vals['name']})
    #         so.write(vals)
    #         return so
    @api.model
    def create(self,vals):
        # function overwrites create method and auto generate request no.
        so = super(tour_booking, self).create(vals)
        if not vals['itinary_id'] and 'itinary_id' in vals:
            print("ooooooooooooooooooo")
            return so
        else:
            req_no = self.env['ir.sequence'].next_by_code('custom.tour.booking')
            print("req_no-------------------",req_no)

            so.name = req_no
            print("so.name----------------------",so.name)
            return so

    # def create(self, cr, uid, vals, context=None):
    #     # function overwrites create method and auto generate request no.
    #     so = super(tour_booking, self).create(cr, uid, vals, context=context)
    #     if not vals['itinary_id'] and vals.has_key('itinary_id'):
    #         return so
    #     else:
    #         req_no = self.pool.get('ir.sequence').get(cr,uid,'custom.tour.booking'),
    #         vals['name'] = req_no[0]
    #         vals.update({'name': vals['name']})
    #         self.write(cr, uid, so, vals)
    #         return so
    #
    
    def create_order(self):
        for obj in self:
            boking_id = super(tour_booking, self).create_order()
            if not obj.itinary_id:
                return boking_id
            else:
                # if obj.tour_sale_order_ids:
                #     for line in obj.tour_sale_order_ids[0].order_line:
                #         # print("line--------------------------", line)
                #         #
                #         # print("dec--------------------------", dec)
                #         # obj.tour_sale_order_ids[0]
                #         # print("obj.tour_sale_order_ids[0].write({'name': dec})",
                #         #       obj.tour_sale_order_ids[0].write({'name': dec}))
                return boking_id
    
#     def create_order(self, cr, uid, ids, *args):
#         for obj in self.browse(cr,uid,ids):
#             boking_id = super(tour_booking, self).create_order(cr, uid, [obj.id], *args)
#             if not obj.itinary_id:
#                 return boking_id
#             else:
#                 if obj.tour_sale_order_ids:
#                     for line in obj.tour_sale_order_ids[0].order_line:
#                         dec = line.product_id.name + '( ' + line.name + ' )'
#                         self.pool.get('sale.order.line').write(cr,uid,obj.tour_sale_order_ids[0].id,{'name': dec}),
#                 return boking_id
            
    
    def _get_total_amt(self):
        res = {}
        obj = self[0]
        adult_tour_cost = 0.00
        child_tour_cost = 0.00
        for tour_line in obj.tour_id.tour_date_lines:
            if tour_line.id == obj.tour_dates_id.id:
                if obj.itinary_id:
                    adult_tour_cost = get_price(self,obj.pricelist_id.id, tour_line.adult_cost_price)
                    child_tour_cost = get_price(self, obj.pricelist_id.id, tour_line.child_cost_price)
                else:
                    adult_tour_cost = get_price(self,obj.pricelist_id.id, tour_line.adult_cost_price)
                    child_tour_cost = get_price(self, obj.pricelist_id.id, tour_line.child_cost_price)
        adult_person = obj.adult 
        child_person = obj.child
        tour_cost = (adult_person * adult_tour_cost) + (child_person * child_tour_cost)
        ins_amt = 0.00
        ins_total = 0.00
        for line in obj.insurance_line_ids:
            ins_total = line._get_insurance_cost()
            ins_amt = ins_amt + ins_total[line.id]
        total = tour_cost + ins_amt
        res[obj.id] = total 
        return res
    
#     def _get_total_amt(self):
#         res = {}
#         total = 0
#         obj = self.browse(cr, uid, ids)[0]
#         adult_tour_cost = 0.00
#         child_tour_cost = 0.00
#         for tour_line in obj.tour_id.tour_date_lines:
#             if tour_line.id == obj.tour_dates_id.id:
#                 if obj.itinary_id:
#                     adult_tour_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, tour_line.adult_cost_price)
#                     child_tour_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, tour_line.child_cost_price)
#                 else:
#                     adult_tour_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, tour_line.adult_cost_price)
#                     child_tour_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, tour_line.child_cost_price)
#         adult_person = obj.adult 
#         child_person = obj.child
#         tour_cost = (adult_person * adult_tour_cost) + (child_person * child_tour_cost)
#         ins_amt = 0.00
#         ins_total = 0.00
#         for line in obj.insurance_line_ids:
#             ins_total = self.pool.get('tour.insurance.line')._get_insurance_cost(cr,uid,[line.id],args1,args2,context=None)
#             ins_amt = ins_amt + ins_total[line.id]
#         total = tour_cost + ins_amt
#         res[obj.id] = total 
#         return res

   
    def _get_total_amt1(self):
        res = {}
        obj = self[0]
        adult_tour_cost = 0.00
        child_tour_cost = 0.00
        for tour_line in obj.tour_id.tour_date_lines:
            if tour_line.id == obj.tour_dates_id.id:
                if obj.itinary_id:
                    adult_tour_cost = get_price(self, obj.pricelist_id.id, tour_line.adult_cost_price)
                    child_tour_cost = get_price(self, obj.pricelist_id.id, tour_line.child_cost_price)
                else:
                    adult_tour_cost = get_price(self, obj.pricelist_id.id, tour_line.adult_cost_price)
                    child_tour_cost = get_price(self, obj.pricelist_id.id, tour_line.child_cost_price)
        adult_person = obj.adult 
        child_person = obj.child
        tour_cost = (adult_person * adult_tour_cost) + (child_person * child_tour_cost)
        ins_amt = 0.00
        ins_total = 0.00
        for line in obj.insurance_line_ids:
            ins_total = line._get_insurance_cost()
            ins_amt = ins_amt + ins_total[line.id]
        total = tour_cost + ins_amt
        res[obj.id] = total 
        return res
    
#     def _get_total_amt1(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         total = 0
#         obj = self.browse(cr, uid, ids)[0]
#         adult_tour_cost = 0.00
#         child_tour_cost = 0.00
#         for tour_line in obj.tour_id.tour_date_lines:
#             if tour_line.id == obj.tour_dates_id.id:
#                 if obj.itinary_id:
#                     adult_tour_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, tour_line.adult_cost_price)
#                     child_tour_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, tour_line.child_cost_price)
#                 else:
#                     adult_tour_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, tour_line.adult_cost_price)
#                     child_tour_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, tour_line.child_cost_price)
#         adult_person = obj.adult 
#         child_person = obj.child
#         tour_cost = (adult_person * adult_tour_cost) + (child_person * child_tour_cost)
#         ins_amt = 0.00
#         ins_total = 0.00
#         for line in obj.insurance_line_ids:
#             ins_total = self.pool.get('tour.insurance.line')._get_insurance_cost(cr,uid,[line.id],args1,args2,context=None)
#             ins_amt = ins_amt + ins_total[line.id]
#         total = tour_cost + ins_amt
#         res[obj.id] = total 
#         return res
    
    
    @api.multi
    def confirm_booking(self):
        tot_person = 0

        for obj in self:
            if not obj.itinary_id:
                print("lk---------------------------------")
                boking_id = super(tour_booking, self).confirm_booking()
                return True
            else:
                tot_person = obj.adult + obj.child
                percen = float(obj.payment_policy_id.before_book_date_perc) / 100
                payment_amt =float(obj.total_amt) * percen
                actual_pay = float(obj.total_amt) - payment_amt 
                
                for i in range(0,len(obj.tour_sale_order_ids)):
                    if obj.tour_sale_order_ids[i].state == 'draft':
                        raise Warning(' Please Confirm The Sale Order Before Booking')
                seats = 0
                person = 0  
                tour_booking_flag = False
                for i in range(0,len(obj.tour_booking_invoice_ids)):
                    if obj.tour_booking_invoice_ids[i].state == 'draft':
                        raise Warning(' Please Validate The Invoice Before Booking')
                    
                    for line in obj.tour_id.tour_date_lines:
                        if line.season_id.id == obj.season_id.id:
                            if line.book_date and line.book_date.strftime('%Y-%m-%d') > time.strftime('%Y-%m-%d'):
                                if obj.tour_booking_invoice_ids[i].residual > actual_pay:
                                    raise Warning(' Please Pay The Booking Amount')
                                seats = line.available_seat
                                if seats == 0:
                                    raise Warning(' No Seats Available')
                                person = seats - tot_person
                                line.write({'available_seat':person})
                                tour_booking_flag = True
                            else:
                                raise UserError('Tour Booking Is Closed')
                self._cr.execute('insert into tour_booking_customer_rel(tour_booking_customer_id,tour_id) values (%s,%s)'%(obj.tour_id.id, obj.id))
                invoice_addr_id = False
                self._cr.execute("""select id from product_template where name='Passport'""")                        
                p_id = self._cr.fetchone()
                self._cr.execute("""select id from product_template where name='Visa'""")                        
                v_id = self._cr.fetchone()
                self._cr.execute("""select id from service_scheme where name='Regular'""")                        
                s_id = self._cr.fetchone()
                self._cr.execute("""select service_cost from service_scheme where name='Regular'""")                        
                s_cost = self._cr.fetchone()
                pricelist_id = obj.pricelist_id.id
                s_cost = get_price(self,obj.pricelist_id.id, s_cost[0])
                for hot_line in obj.itinary_id.hotel_planer_ids:
                    search_id = self.env['hotel.information'].search(
                        [('hotel_id', '=', hot_line.hotel_id.id), ('state', '=', 'confirm')], limit=1)
                    vals = {
                           'customer_id': obj.customer_id.id,
                           'current_date':obj.current_date,
                           'email_id':obj.email_id,
                           'mobile':obj.mobile1,
                           'adult':obj.adult,
                           'child':obj.child,
                           'hotel_type_id':hot_line.hotel_type_id.id,
                           'hotel_id':search_id.id,
                           'room_type_id':hot_line.room_type_id.id,
                           'room_rent':hot_line.supplier_price,
                           'hotel_rent':hot_line.customer_price,
                           'room_required':hot_line.room_req,
                           'tour_id':obj.tour_id.id,
                           'tour_book_id':obj.id,
                           'tour_start_date':obj.tour_dates_id.id,
                           'destination_id':hot_line.destination_id.id,
                           'pricelist_id':pricelist_id,
                        }
                    hot_id = self.env['tour.hotel.reservation'].create(vals)
                    for customer_line in obj.tour_customer_ids:
                        if customer_line.h_flag == True:
                            cust_vals = {
                                         'name':customer_line.name,
                                         'partner_id':customer_line.partner_id.id,
                                         'type':customer_line.type,
                                         'gender':customer_line.gender,
                                         'hotel_res_id':hot_id.id,
                                         }
                            customer_id = self.env['tour.customer.details'].create(cust_vals)
                if obj.itinary_id.travel_planer_ids:
                    for travel_line in obj.itinary_id.travel_planer_ids:
                        vals ={
                               'customer_id': obj.customer_id.id,
                               'current_date':obj.current_date,
                               'email_id':obj.email_id,
                               'mobile':obj.mobile1,
                               'adult':obj.adult,
                               'child':obj.child,
                               'transport_id':travel_line.transport_id.id,
                               'transport_carrier_id':travel_line.transport_carrier_id.id,
                               'transport_type_id':travel_line.transport_type_id.id,
                               'travel_class_id':travel_line.travel_class_id.id,
                               'from_destination_id':travel_line.from_destination_id.id,
                               'to_destination_id':travel_line.to_destination_id.id,
                               'tour_id':obj.tour_id.id,
                               'tour_book_id':obj.id,
                               'start_date':obj.tour_dates_id.id,
                               'pricelist_id':pricelist_id,
                                }
                        trans_id = self.env['transport.book'].create(vals)
                        for customer_line in obj.tour_customer_ids:
                            if customer_line.t_flag == True:
                                cust_vals = {
                                             'name':customer_line.name,
                                             'partner_id':customer_line.partner_id.id,
                                             'type':customer_line.type,
                                             'gender':customer_line.gender,
                                             'customer_id':trans_id.id,
                                             }
                                self.env['tour.customer.details'].create(cust_vals)
                mobile_data = ''
                email_data = ''
                for cust_line in obj.tour_customer_ids:
                    if cust_line.i_flag == True:
                        print("Insurance")
                    if cust_line.v_flag == True:
                            country_list = []
                            visa_type_list = []
                            for visa_obj in obj.tour_id.tour_destination_lines:
                                if visa_obj.is_visa == True:
                                    if not visa_obj.country_id.id in country_list:
                                        country_list.append(visa_obj.country_id.id)
                                        visa_type_list.append(visa_obj.visa_type)
                            lenth = len(country_list)
                            for i in range(0,lenth):
                                if visa_type_list[i] == 'single':
                                    self._cr.execute("""select id from visa_scheme where name='Tourist Visa(Single Entry)'""")                        
                                    visa_id = self._cr.fetchone()
                                    self._cr.execute("""select service_cost from visa_scheme where name='Tourist Visa(Single Entry)'""")                        
                                    visa_cost = self._cr.fetchone()
                                    visa_cost = get_price(self, obj.pricelist_id.id, visa_cost[0])
                                else:
                                    self._cr.execute("""select id from visa_scheme where name='Tourist Visa(Multiple Entry)'""")                        
                                    visa_id = self._cr.fetchone()
                                    self._cr.execute("""select service_cost from visa_scheme where name='Tourist Visa(Multiple Entry)'""")                        
                                    visa_cost = self._cr.fetchone()
                                    visa_cost = get_price(self,obj.pricelist_id.id, visa_cost[0])
                                vals ={
                                       'customer_id': cust_line.partner_id.id,
                                       'current_date':obj.current_date,
                                       'email_id':cust_line.partner_id.email,
                                       'mobile':cust_line.partner_id.mobile,
                                       'country_id':country_list[i],
                                       'product_id':v_id[0],
                                       'scheme_id':visa_id[0],
                                       'service_charge':visa_cost,
                                       'tour_book_id':obj.id,
                                       'tour_id':obj.tour_id.id,
                                       'tour_date':obj.tour_dates_id.name,
                                       'pricelist_id':pricelist_id,
                                       }
                                self.env['visa.booking'].create(vals)
                    if cust_line.p_flag == True:
                        vals ={
                               'customer_id': cust_line.partner_id.id,
                               'current_date':obj.current_date,
                               'email_id':cust_line.partner_id.email,
                               'mobile':cust_line.partner_id.mobile,
                               'product_id':p_id[0],
                               'scheme_id':s_id[0],
                               'service_charge':s_cost,
                               'tour_book_id':obj.id,
                               'tour_id':obj.tour_id.id,
                               'tour_date':obj.tour_dates_id.name,
                               'pricelist_id':pricelist_id,
                            }
                        self.env['passport.booking'].create(vals)
                        
            self.write({'state':'booked'})
            return True
    
#     def confirm_booking(self, cr, uid, ids, *args):
#         tot_person = 0
#         for obj in self.browse(cr,uid,ids):
#             if not obj.itinary_id:
#                 boking_id = super(tour_booking, self).confirm_booking(cr, uid, [obj.id], *args)
#                 return True
#             else:
#                 tot_person = obj.adult + obj.child
#                 payment_amt = 0.0
#                 percen = 0.0
#                 percen = float(obj.payment_policy_id.before_book_date_perc) / 100
#                 payment_amt =float(obj.total_amt) * percen
#                 actual_pay = float(obj.total_amt) - payment_amt 
#                 
#                 for i in range(0,len(obj.tour_sale_order_ids)):
#                     if obj.tour_sale_order_ids[i].state == 'draft':
#                         raise osv.except_osv(_('Error !'), _(' Please Confirm The Sale Order Before Booking'))
#                 seats = 0
#                 person = 0  
#                 tour_booking_flag = False
#                 for i in range(0,len(obj.tour_booking_invoice_ids)):
#                     if obj.tour_booking_invoice_ids[i].state == 'draft':
#                         raise osv.except_osv(_('Error !'), _(' Please Validate The Invoice Before Booking'))
#                     
#                     for line in obj.tour_id.tour_date_lines:
#                         if line.season_id.id == obj.season_id.id:
#                             if line.book_date > time.strftime('%Y-%m-%d'):
#                                 if obj.tour_booking_invoice_ids[i].residual > actual_pay:
#                                     raise osv.except_osv(_('Error !'), _(' Please Pay The Booking Amount'))
#                                 seats = line.available_seat
#                                 if seats == 0:
#                                     raise osv.except_osv(_('Error !'), _(' No Seats Available'))
#                                 person = seats - tot_person
#                                 self.pool.get('tour.dates').write(cr,uid,line.id,{'available_seat':person})
#                                 tour_booking_flag = True
#                             else:
#                                 raise osv.except_osv(_('Error !'), _('Tour Booking Is Closed'))
#                 cr.execute('insert into tour_booking_customer_rel(tour_booking_customer_id,tour_id) values (%s,%s)', (obj.tour_id.id, obj.id))
#                 print obj.tour_id.tour_hotel_info_lines,"obj.tour_id.tour_hotel_info_lines"
#                 invoice_addr_id = False
#                 cr.execute("""select id from product_template where name='Passport'""")                        
#                 p_id = cr.fetchone()
#                 print "Product",p_id[0]
#                 cr.execute("""select id from product_template where name='Visa'""")                        
#                 v_id = cr.fetchone()
#                 print "Visa",v_id[0]
#                 cr.execute("""select id from service_scheme where name='Regular'""")                        
#                 s_id = cr.fetchone()
#                 print "Scheme",s_id[0]
#                 cr.execute("""select service_cost from service_scheme where name='Regular'""")                        
#                 s_cost = cr.fetchone()
#                 pricelist_id = obj.pricelist_id.id
#                 s_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, s_cost[0])
#                 for hot_line in obj.itinary_id.hotel_planer_ids:
#                     print hot_line,"hot_line"
#                     vals = {
#                            'customer_id': obj.customer_id.id,
#                            'current_date':obj.current_date,
#                            'email_id':obj.email_id,
#                            'mobile':obj.mobile1,
#                            'adult':obj.adult,
#                            'child':obj.child,
#                            'hotel_type_id':hot_line.hotel_type_id.id,
#                            'hotel_id':hot_line.hotel_id.id,
#                            'room_type_id':hot_line.room_type_id.id,
#                            'room_rent':hot_line.supplier_price,
#                            'hotel_rent':hot_line.customer_price,
#                            'room_required':hot_line.room_req,
#                            'tour_id':obj.tour_id.id,
#                            'tour_book_id':obj.id,
#                            'tour_start_date':obj.tour_dates_id.id,
#                            'destination_id':hot_line.destination_id.id,
#                            'pricelist_id':pricelist_id,
#                             }
#                     hot_id = self.pool.get('tour.hotel.reservation').create(cr,uid,vals)
#                     for customer_line in obj.tour_customer_ids:
#                         if customer_line.h_flag == True:
#                             print "Hotel Booking"
#                             cust_vals = {
#                                          'name':customer_line.name,
#                                          'partner_id':customer_line.partner_id.id,
#                                          'type':customer_line.type,
#                                          'gender':customer_line.gender,
#                                          'hotel_res_id':hot_id,
#                                          }
#                             customer_id = self.pool.get('tour.customer.details').create(cr,uid,cust_vals)
#                             print customer_id,"customer_id"
#                 if obj.itinary_id.travel_planer_ids:
#                     for travel_line in obj.itinary_id.travel_planer_ids:
#                         vals ={
#                                'customer_id': obj.customer_id.id,
#                                'current_date':obj.current_date,
#                                'email_id':obj.email_id,
#                                'mobile':obj.mobile1,
#                                'adult':obj.adult,
#                                'child':obj.child,
#                                'transport_id':travel_line.transport_id.id,
#                                'transport_carrier_id':travel_line.transport_carrier_id.id,
#                                'transport_type_id':travel_line.transport_type_id.id,
#                                'travel_class_id':travel_line.travel_class_id.id,
#                                'from_destination_id':travel_line.from_destination_id.id,
#                                'to_destination_id':travel_line.to_destination_id.id,
#                                'tour_id':obj.tour_id.id,
#                                'tour_book_id':obj.id,
#                                'start_date':obj.tour_dates_id.id,
#                                'pricelist_id':pricelist_id,
#                                 }
#                         print "Transport vals",vals
#                         trans_id = self.pool.get('transport.book').create(cr,uid,vals)
#                         for customer_line in obj.tour_customer_ids:
#                             if customer_line.t_flag == True:
#                                 print "Transport Booking"
#                                 cust_vals = {
#                                              'name':customer_line.name,
#                                              'partner_id':customer_line.partner_id.id,
#                                              'type':customer_line.type,
#                                              'gender':customer_line.gender,
#                                              'customer_id':trans_id,
#                                              }
#                                 print "cust Vals",cust_vals
#                                 self.pool.get('tour.customer.details').create(cr,uid,cust_vals)
#                 mobile_data = ''
#                 email_data = ''
#                 for cust_line in obj.tour_customer_ids:
#                     if cust_line.i_flag == True:
#                             print "Insurance"
#                     if cust_line.v_flag == True:
#                             print "Visa"
#                             country_list = []
#                             visa_type_list = []
#                             for visa_obj in obj.tour_id.tour_destination_lines:
#                                 if visa_obj.is_visa == True:
#                                     if not visa_obj.country_id.id in country_list:
#                                         country_list.append(visa_obj.country_id.id)
#                                         visa_type_list.append(visa_obj.visa_type)
#                             lenth = len(country_list)
#                             for i in range(0,lenth):
#                                 print visa_type_list[i],"visa_type_list[i]"
#                                 if visa_type_list[i] == 'single':
#                                     cr.execute("""select id from visa_scheme where name='Tourist Visa(Single Entry)'""")                        
#                                     visa_id = cr.fetchone()
#                                     print "Scheme",visa_id[0]
#                                     cr.execute("""select service_cost from visa_scheme where name='Tourist Visa(Single Entry)'""")                        
#                                     visa_cost = cr.fetchone()
#                                     visa_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, visa_cost[0])
#                                 else:
#                                     cr.execute("""select id from visa_scheme where name='Tourist Visa(Multiple Entry)'""")                        
#                                     visa_id = cr.fetchone()
#                                     print "Scheme",visa_id[0]
#                                     cr.execute("""select service_cost from visa_scheme where name='Tourist Visa(Multiple Entry)'""")                        
#                                     visa_cost = cr.fetchone()
#                                     visa_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, visa_cost[0])
#                                 vals ={
#                                        'customer_id': cust_line.partner_id.id,
#                                        'current_date':obj.current_date,
#                                        'email_id':cust_line.partner_id.email,
#                                        'mobile':cust_line.partner_id.mobile,
#                                        'country_id':country_list[i],
#                                        'product_id':v_id[0],
#                                        'scheme_id':visa_id[0],
#                                        'service_charge':visa_cost,
#                                        'tour_book_id':obj.id,
#                                        'tour_id':obj.tour_id.id,
#                                        'tour_date':obj.tour_dates_id.name,
#                                        'pricelist_id':pricelist_id,
#                                        }
#                                 print "vals",vals
#                                 self.pool.get('visa.booking').create(cr,uid,vals)
#                     if cust_line.p_flag == True:
#                         print "Passport"
#                         vals ={
#                                'customer_id': cust_line.partner_id.id,
#                                'current_date':obj.current_date,
#                                'email_id':cust_line.partner_id.email,
#                                'mobile':cust_line.partner_id.mobile,
#                                'product_id':p_id[0],
#                                'scheme_id':s_id[0],
#                                'service_charge':s_cost,
#                                'tour_book_id':obj.id,
#                                'tour_id':obj.tour_id.id,
#                                'tour_date':obj.tour_dates_id.name,
#                                'pricelist_id':pricelist_id,
#                             }
#                         print "vals",vals
#                         self.pool.get('passport.booking').create(cr,uid,vals)
#                         
#             self.write(cr, uid, ids, {'state':'booked'})
#             return True
                    
                
     

class tour_destination_line(models.Model):
    _inherit = "tour.destination.line"
    _description = "Tour Destination Lines"
    
    
    def create(self, vals): 
        # function overwrites create method and auto generate request no. 
        so = super(tour_destination_line, self).create(vals)
        if ('itinarary_id' in vals and vals['itinarary_id']) and ('is_visa' in vals and vals.has_key('visa_type') and vals['visa_type'] and vals['is_visa']):
            categ_id = self.env['product.category'].search([('name','=','Visa Services')])
            visa_id = self.env['product.product'].search([('name', '=', 'Visa'),('type', '=', 'service'),('categ_id', '=', categ_id[0])])
            if not visa_id:
                raise UserError('Product Visa is not Found.')
            res = visa_id[0]
            custom_id = self.env['custom.tour.itinarary'].browse(vals['itinarary_id'])
            sale_tax_ids = self.env['account.fiscal.position'].map_tax(res.taxes_id)
            pur_tax_ids = self.env['account.fiscal.position'].map_tax(res.supplier_taxes_id) 
            created_visa_id = self.env['visa.costing.line'].create({'itinary_id': vals['itinarary_id'],
                                                                    'name':visa_id[0],
                                                                    'country_id': vals['country_id'],
                                                                    'visa_type':vals['visa_type'],
                                                                    'total_person':custom_id.total_seat,
                                                                    'destination_id':so.id,
                                                                    'sale_tax_ids':[(6,0,sale_tax_ids)],
                                                                    'pur_tax_ids':[(6,0,pur_tax_ids)]})
        return so
    
#     def create(self, cr, uid, vals, context=None): 
#         # function overwrites create method and auto generate request no. 
#         print vals,"valssssssss"
#         so = super(tour_destination_line, self).create(cr, uid, vals, context=context)
#         if (vals.has_key('itinarary_id') and vals['itinarary_id']) and (vals.has_key('is_visa') and vals.has_key('visa_type') and vals['visa_type'] and vals['is_visa']):
#             categ_id = self.pool.get('product.category').search(cr, uid, [('name','=','Visa Services')])
#             visa_id = self.pool.get('product.product').search(cr, uid, [('name', '=', 'Visa'),('type', '=', 'service'),('categ_id', '=', categ_id[0])])
#             if not visa_id:
#                 raise osv.except_osv(_('Error !'), _('Product Visa is not Found.'))
#             res = self.pool.get('product.product').browse(cr, uid, visa_id[0])
#             fpos = False
#             custom_id = self.pool.get('custom.tour.itinarary').browse(cr, uid, vals['itinarary_id'])
#             sale_tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, res.taxes_id)
#             pur_tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, res.supplier_taxes_id) 
#             created_visa_id = self.pool.get('visa.costing.line').create(cr, uid, {'itinary_id': vals['itinarary_id'], 'name':visa_id[0], 'country_id': vals['country_id'],
#                                                                               'visa_type':vals['visa_type'], 'total_person':custom_id.total_seat,'destination_id':so,
#                                                                               'sale_tax_ids':[(6,0,sale_tax_ids)],'pur_tax_ids':[(6,0,pur_tax_ids)]})
#         return so
    
    
    @api.model
    def write(self,vals):
        """
        Overriding the write method
        """
        for obj in self:
            categ_id = self.env['product.category'].search([('name','=','Visa Services')])
            visa_id = self.env['product.product'].search([('name', '=', 'Visa'),('type', '=', 'service'),('categ_id', '=', categ_id[0].id)])
            if not visa_id:
                raise UserError('Product Visa is not Found.')
            if obj.itinarary_id:
                if 'is_visa' in vals and vals['is_visa'] and 'visa_type' in vals and vals['visa_type']:
                    if not (vals['is_visa'] == obj.is_visa and vals['visa_type'] == obj.visa_type):
                        res = visa_id[0]
                        sale_tax_ids = self.env['account.fiscal.position'].map_tax(res.taxes_id)
                        pur_tax_ids = self.env['account.fiscal.position'].map_tax(res.supplier_taxes_id) 
                        created_visa_id = self.env['visa.costing.line'].create({'itinary_id': obj.itinarary_id.id,
                                                                                'name':visa_id[0].id,
                                                                                'country_id': obj.country_id.id,
                                                                                'visa_type':vals['visa_type'],
                                                                                'total_person':obj.itinarary_id.total_seat,
                                                                                'destination_id':obj.id,
                                                                                'sale_tax_ids':[(6,0,sale_tax_ids)],
                                                                                'pur_tax_ids':[(6,0,pur_tax_ids)]})
                    if (vals['is_visa'] == obj.is_visa and vals['visa_type'] != obj.visa_type):
                        visa_costing = self.env['visa.costing.line'].search([('itinary_id', '=', obj.itinarary_id.id),('name.id', '=', visa_id[0]),('country_id', '=', obj.country_id.id),('destination_id', '=', obj.id)])
                        if visa_costing:
                            visa_unlink = visa_costing.unlink()
                        res = visa_id[0]
                        sale_tax_ids = self.env['account.fiscal.position'].map_tax(res.taxes_id)
                        pur_tax_ids = self.env['account.fiscal.position'].map_tax(res.supplier_taxes_id) 
                        created_visa_id = self.env['visa.costing.line'].create({'itinary_id': obj.itinarary_id.id,
                                                                                'name':visa_id[0].id,
                                                                                'country_id': obj.country_id.id,
                                                                                'visa_type':vals['visa_type'],
                                                                                'total_person':obj.itinarary_id.total_seat,
                                                                                'destination_id':obj.id,
                                                                                'sale_tax_ids':[(6,0,sale_tax_ids)],
                                                                                'pur_tax_ids':[(6,0,pur_tax_ids)]})
                if 'is_visa' in vals and vals['is_visa'] and ('visa_type' not in  vals) and obj.visa_type:
                    res = visa_id[0]
                    sale_tax_ids = self.env['account.fiscal.position'].map_tax(res.taxes_id)
                    pur_tax_ids = self.env['account.fiscal.position'].map_tax(res.supplier_taxes_id) 
                    created_visa_id = self.env['visa.costing.line'].create({'itinary_id': obj.itinarary_id.id,
                                                                            'name':visa_id[0].id,
                                                                            'country_id': obj.country_id.id,
                                                                            'visa_type':obj.visa_type,
                                                                            'total_person':obj.itinarary_id.total_seat,'destination_id':obj.id,
                                                                            'sale_tax_ids':[(6,0,sale_tax_ids)],
                                                                            'pur_tax_ids':[(6,0,pur_tax_ids)]})
                if 'is_visa' in vals and (vals['is_visa']== False):
                    visa_costing = self.env['visa.costing.line'].search([('itinary_id', '=', obj.itinarary_id.id),('name.id', '=', visa_id[0].id),('country_id', '=', obj.country_id.id),('destination_id', '=', obj.id)])
                    if visa_costing:
                        visa_unlink = visa_costing.unlink()
        return super(tour_destination_line, self).write(vals)
    
#     def write(self, cr, uid, ids, vals, context=None):
#         """
#         Overriding the write method
#         """
#         for obj in self.browse(cr, uid, ids):
#             categ_id = self.pool.get('product.category').search(cr, uid, [('name','=','Visa Services')])
#             visa_id = self.pool.get('product.product').search(cr, uid, [('name', '=', 'Visa'),('type', '=', 'service'),('categ_id', '=', categ_id[0])])
#             if not visa_id:
#                 raise osv.except_osv(_('Error !'), _('Product Visa is not Found.'))
#             if obj.itinarary_id:
#                 if vals.has_key('is_visa') and vals['is_visa'] and vals.has_key('visa_type') and vals['visa_type']:
#                     if not (vals['is_visa'] == obj.is_visa and vals['visa_type'] == obj.visa_type):
#                         res = self.pool.get('product.product').browse(cr, uid, visa_id[0])
#                         fpos = False
#                         sale_tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, res.taxes_id)
#                         pur_tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, res.supplier_taxes_id) 
#                         created_visa_id = self.pool.get('visa.costing.line').create(cr, uid, {'itinary_id': obj.itinarary_id.id, 'name':visa_id[0], 'country_id': obj.country_id.id,
#                                                                                           'visa_type':vals['visa_type'], 'total_person':obj.itinarary_id.total_seat,'destination_id':obj.id,
#                                                                                           'sale_tax_ids':[(6,0,sale_tax_ids)],'pur_tax_ids':[(6,0,pur_tax_ids)]})
#                     if (vals['is_visa'] == obj.is_visa and vals['visa_type'] != obj.visa_type):
#                         visa_costing = self.pool.get('visa.costing.line').search(cr, uid, [('itinary_id', '=', obj.itinarary_id.id),('name.id', '=', visa_id[0]),('country_id', '=', obj.country_id.id),('destination_id', '=', obj.id)])
#                         if visa_costing:
#                             visa_unlink = self.pool.get('visa.costing.line').unlink(cr, uid,visa_costing)
#                         res = self.pool.get('product.product').browse(cr, uid, visa_id[0])
#                         fpos = False
#                         sale_tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, res.taxes_id)
#                         pur_tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, res.supplier_taxes_id) 
#                         created_visa_id = self.pool.get('visa.costing.line').create(cr, uid, {'itinary_id': obj.itinarary_id.id, 'name':visa_id[0], 'country_id': obj.country_id.id,
#                                                                                           'visa_type':vals['visa_type'], 'total_person':obj.itinarary_id.total_seat,'destination_id':obj.id,
#                                                                                           'sale_tax_ids':[(6,0,sale_tax_ids)],'pur_tax_ids':[(6,0,pur_tax_ids)]})
#                 if vals.has_key('is_visa') and vals['is_visa'] and ( not vals.has_key('visa_type')) and obj.visa_type:
#                     res = self.pool.get('product.product').browse(cr, uid, visa_id[0])
#                     fpos = False
#                     sale_tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, res.taxes_id)
#                     pur_tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, res.supplier_taxes_id) 
#                     created_visa_id = self.pool.get('visa.costing.line').create(cr, uid, {'itinary_id': obj.itinarary_id.id, 'name':visa_id[0], 'country_id': obj.country_id.id,
#                                                                                       'visa_type':obj.visa_type, 'total_person':obj.itinarary_id.total_seat,'destination_id':obj.id,
#                                                                                       'sale_tax_ids':[(6,0,sale_tax_ids)],'pur_tax_ids':[(6,0,pur_tax_ids)]})
#                 if vals.has_key('is_visa') and (vals['is_visa']== False):
#                     visa_costing = self.pool.get('visa.costing.line').search(cr, uid, [('itinary_id', '=', obj.itinarary_id.id),('name.id', '=', visa_id[0]),('country_id', '=', obj.country_id.id),('destination_id', '=', obj.id)])
#                     if visa_costing:
#                         visa_unlink = self.pool.get('visa.costing.line').unlink(cr, uid,visa_costing)
#         return super(tour_destination_line, self).write(cr, uid, ids, vals, context=context)   
    
   
    @api.multi
    def unlink(self):
        """
        Allows to delete Product Category which are not defined in demo data
        """
        for obj in self:
            categ_id = self.env['product.category'].search([('name','=','Visa Services')])
            visa_id = self.env['product.product'].search([('name', '=', 'Visa'),('type', '=', 'service'),('categ_id', '=', categ_id[0].id)])
            if not visa_id:
                raise UserError('Product Visa is not Found.')
            visa_costing = self.env['visa.costing.line'].search([('itinary_id', '=', obj.itinarary_id.id),('name.id', '=', visa_id[0].id),('country_id', '=', obj.country_id.id),('destination_id', '=', obj.id)])
            if visa_costing:
                visa_unlink = visa_costing.unlink()
                
        ## added by indrajeet for soloving issue of delete the records and saving reocrds................
        search_id = self.env['tour.destination.hotel.line'].search([('destination_line_id','=', self._ids)])
        if search_id:
            for id in search_id:
                id.unlink()
        return super(tour_destination_line, self).unlink()
    
#     def unlink(self, cr, uid, ids, context):
#         """
#         Allows to delete Product Category which are not defined in demo data
#         """
#         for obj in self.browse(cr, uid, ids, context = context):
#             categ_id = self.pool.get('product.category').search(cr, uid, [('name','=','Visa Services')])
#             visa_id = self.pool.get('product.product').search(cr, uid, [('name', '=', 'Visa'),('type', '=', 'service'),('categ_id', '=', categ_id[0])])
#             if not visa_id:
#                 raise osv.except_osv(_('Error !'), _('Product Visa is not Found.'))
#             visa_costing = self.pool.get('visa.costing.line').search(cr, uid, [('itinary_id', '=', obj.itinarary_id.id),('name.id', '=', visa_id[0]),('country_id', '=', obj.country_id.id),('destination_id', '=', obj.id)])
#             if visa_costing:
#                 visa_unlink = self.pool.get('visa.costing.line').unlink(cr, uid,visa_costing)
#                 
#         ## added by indrajeet for soloving issue of delete the records and saving reocrds................
#         search_id = self.pool.get('tour.destination.hotel.line').search(cr, uid, [('destination_line_id','=', ids)])
#         if search_id:
#             for id in search_id:
#                 self.pool.get('tour.destination.hotel.line').unlink(cr, uid, id)
#         return super(tour_destination_line, self).unlink(cr, uid, ids, context = context)

    
    
    itinarary_id = fields.Many2one('custom.tour.itinarary','Itinerary Ref')
    
    


class tour_cost_exclude_facility(models.Model):
    _inherit = "tour.cost.exclude.facility"
    _description = "tour cost exclude facility"

    itinary_id = fields.Many2one('custom.tour.itinarary','Itinerary Ref')

    


class tour_cost_include_facility(models.Model):
    _inherit = "tour.cost.include.facility"
    _description = "tour cost include facility"

    itinary_id = fields.Many2one('custom.tour.itinarary','Itinerary Ref')
    



class sites_costing_line(models.Model):
    _name = "sites.costing.line"
    _description = "Tour Destination Lines"

    
    ## updated code of _get_total method ................
    @api.depends('new_sale_price','new_cost_price')
    def _get_total_amt(self):
        # res = {}
        # cost_price = sale_price = total_cost_price = total_sale_price = 0.00
        for obj in self:
            obj.cost_price = get_price(self,  obj.itinary_id.pricelist_id.id, float(obj.new_cost_price))
            obj.sale_price = get_price(self, obj.itinary_id.pricelist_id.id, float(obj.new_sale_price))
            total_cost_p = float(obj.new_cost_price) * (obj.itinary_id.adult + obj.itinary_id.child)
            total_sale_p = float(obj.new_sale_price) * (obj.itinary_id.adult + obj.itinary_id.child)

            obj.total_cost_price = get_price(self, obj.itinary_id.pricelist_id.id, total_cost_p)
            obj.total_sale_price = get_price(self,  obj.itinary_id.pricelist_id.id, total_sale_p)

        #     record = {
        #         'cost_price':cost_price,
        #         'sale_price':sale_price,
        #         'total_cost_price':total_cost_price,
        #         'total_sale_price':total_sale_price,
        #     }
        #     res[obj.id] = record
        # return res
    
#     ## updated code of _get_total method ................
#     def _get_total_amt(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         cost_price = sale_price = total_cost_price = total_sale_price = 0.00
#         for obj in self.browse(cr,uid,ids):
#             cost_price = get_price(self, cr, uid, ids, obj.itinary_id.pricelist_id.id, float(obj.new_cost_price))
#             sale_price = get_price(self, cr, uid, ids, obj.itinary_id.pricelist_id.id, float(obj.new_sale_price))
#             total_cost_p = float(obj.new_cost_price) * (obj.itinary_id.adult + obj.itinary_id.child)
#             total_sale_p = float(obj.new_sale_price) * (obj.itinary_id.adult + obj.itinary_id.child)
#             
#             total_cost_price = get_price(self, cr, uid, ids, obj.itinary_id.pricelist_id.id, total_cost_p)
#             total_sale_price = get_price(self, cr, uid, ids, obj.itinary_id.pricelist_id.id, total_sale_p)
#             record = {
#                 'cost_price':cost_price,
#                 'sale_price':sale_price,
#                 'total_cost_price':total_cost_price,
#                 'total_sale_price':total_sale_price,
#             }
#             res[obj.id] = record
#         return res
    
    
    
    itinary_id = fields.Many2one('custom.tour.itinarary',string='Itinerary Ref')
    name = fields.Many2one('product.product',string='Sites Name',required=True)
    cost_price = fields.Float(compute=_get_total_amt, store=True, multi='dc', string='Cost Price/ Person', digits=dp.get_precision('Account'))
    sale_price = fields.Float(compute=_get_total_amt,  store=True, multi='dc', string='Sale Price/ Person', digits=dp.get_precision('Account'))
    new_cost_price = fields.Char(string='Cost Price/ Person', size=150)
    new_sale_price = fields.Char(string='Sale Price/ Person', size=150)
    total_cost_price = fields.Float(compute=_get_total_amt, store=True, multi='dc', string='Total Cost Price', digits=dp.get_precision('Account'))
    total_sale_price = fields.Float(compute=_get_total_amt, store=True, multi='dc', string='Total Sale Price', digits=dp.get_precision('Account'))
    sale_tax_ids = fields.Many2many('account.tax', 'sale_sites_tax_line_rel', 'tour_itinary_id', 'tax_id', string='Sale Taxes')
    pur_tax_ids = fields.Many2many('account.tax', 'pur_sites_tax_line_rel', 'tour_itinary_id', 'tax_id', string='Purchase Taxes')
    tour_program_id = fields.Many2one('custom.tour.programme',string='Tour Program ID')
    



class hotel_planer_details(models.Model):
    _name = "hotel.planer.details"
    _description = "hotel planer details"
    
    
    def get_room_req(self):
        """ 
        Gets document number while order in quotation state
        """
        if 'parent_id' in self._context and self._context['parent_id']:
            obj = self.env['custom.tour.itinarary'].browse(self._context['parent_id'])
            if obj:
                return obj.room_req
            else:
                return False
    
#     def get_room_req(self, cr, uid, context=None):
#         """ 
#         Gets document number while order in quotation state
#         """
#         if context.has_key('parent_id') and context['parent_id']:
#             obj = self.pool.get('custom.tour.itinarary').browse(cr,uid,context['parent_id'])
#             if obj:
#                 return obj.room_req
#             else:
#                 return False



    
    
    hotel_planer_id = fields.Many2one('custom.tour.itinarary','Itinerary Ref',required=True)
    name = fields.Char("Sequence",size=3,required=True)
    destination_id = fields.Many2one('tour.destinations','Destination',required=True)
    hotel_type_id = fields.Many2one('hotel.type','Hotel Type',required=True)
    room_type_id = fields.Many2one('product.product',"Room Type",required=True,)
    hotel_id = fields.Many2one('res.partner',"Hotel",required=True,)
    room_req = fields.Integer("No. of Room Required",default=lambda self: self.get_room_req())
    days = fields.Integer("No. of Days to stay",)
    supplier_price = fields.Float("Supplier Rent / Night",required=True,)
    customer_price = fields.Float("Customer Rent / Night",required=True,)
    supplier_price_total = fields.Float("Total Supplier Price",)
    customer_price_total = fields.Float("Total Customer Price",)
    sale_tax_ids = fields.Many2many('account.tax', 'sale_hotel_tax_line_rel', 'tour_itinary_id', 'tax_id', 'Sale Taxes')
    pur_tax_ids = fields.Many2many('account.tax', 'pur_hotel_tax_line_rel', 'tour_itinary_id', 'tax_id', 'Purchase Taxes')
    purches_bol = fields.Boolean('Show Purchase Tax')
    
    
#     _defaults = {
#         'room_req': lambda self,cr,uid,context: self.get_room_req(cr, uid, context),
#     }
    
    @api.depends('hotel_planer_id.pricelist_id')
    @api.onchange('room_type_id', 'hotel_id', 'room_req', 'days')
    def onchange_room_type(self):
        result = {}
        warning = {}
        if not self.hotel_planer_id.pricelist_id:
            raise Warning("PriceList is not Selected !")
        pricelist_obj=self.hotel_planer_id.pricelist_id
        
        if self.room_type_id:
            res = self.room_type_id
            result['sale_tax_ids'] = self.env['account.fiscal.position'].map_tax(res.taxes_id)
            if res.seller_ids:
                for line in res.seller_ids:
                    if line.name.id == self.hotel_id.id:
                            result['customer_price'] = get_price(self, self.hotel_planer_id.pricelist_id.id, line.sale_price)
                            result['supplier_price'] = get_price(self, self.hotel_planer_id.pricelist_id.id, line.price)
                            customer_price = line.sale_price * self.room_req * self.days
                            supplier_price = line.price * self.room_req * self.days
                            result['customer_price_total'] = get_price(self, self.hotel_planer_id.pricelist_id.id, customer_price)
                            result['supplier_price_total'] = get_price(self, self.hotel_planer_id.pricelist_id.id, supplier_price)
                if not result:
                    warn_msg = _("Rate is not define for above Hotel information.")
                    warning = {
                        'title': _('Warning !'),
                        'message': warn_msg
                        }
            else:
                warn_msg = _("Rate is not define for above Hotel information.")
                warning = {
                    'title': _('Warning !'),
                    'message': warn_msg
                    }
        return {'value': result,'warning': warning}
    
#     def onchange_room_type(self, cr, uid, ids, room_type_id, hotel_id, room_req, days, pricelist, context=None):
#         result = {}
#         warning = {}
#         if not pricelist:
#             raise osv.except_osv(_("Warning"),_("PriceList is not Selected !"))
#         pricelist_obj=self.pool.get('product.pricelist').browse(cr,uid,pricelist)
#         
#         if room_type_id:
#             res = self.pool.get('product.product').browse(cr,uid,room_type_id)
#             fpos = False
#             result['sale_tax_ids'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, res.taxes_id)
#             if res.seller_ids:
#                 for line in res.seller_ids:
#                     if line.name.id == hotel_id:
#                             result['customer_price'] = get_price(self, cr, uid, ids, pricelist, line.sale_price)
#                             result['supplier_price'] = get_price(self, cr, uid, ids, pricelist, line.price)
#                             customer_price=line.sale_price * room_req * days
#                             supplier_price=line.price * room_req * days
#                             result['customer_price_total'] = get_price(self, cr, uid, ids, pricelist, customer_price)
#                             result['supplier_price_total'] = get_price(self, cr, uid, ids, pricelist, supplier_price)
#                 if not result:
#                     warn_msg = _("Rate is not define for above Hotel information.")
#                     warning = {
#                         'title': _('Warning !'),
#                         'message': warn_msg
#                         }
#             else:
#                 warn_msg = _("Rate is not define for above Hotel information.")
#                 warning = {
#                     'title': _('Warning !'),
#                     'message': warn_msg
#                     }
#         return {'value': result,'warning': warning}
    
    
    @api.depends('room_type_id')
    @api.onchange('purches_bol')
    def on_change_purchase_bool(self):
        result = {}
        if self.room_type_id and self.purches_bol:
            product_browse = self.room_type_id
            result['pur_tax_ids'] = self.env['account.fiscal.position'].map_tax(product_browse.supplier_taxes_id)
        if self.room_type_id and (not self.purches_bol):
            result['pur_tax_ids'] = []
        return {'value': result}
    
#     def on_change_purchase_bool(self, cr, uid, ids, purches_bol, room_type_id):
#         result = {}
#         if room_type_id and purches_bol:
#             product_browse = self.pool.get('product.product').browse(cr,uid,room_type_id)
#             fpos = False
#             result['pur_tax_ids'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_browse.supplier_taxes_id)
#         if room_type_id and (not purches_bol):
#             result['pur_tax_ids'] = []
#         return {'value': result}
    
    
    @api.depends('room_req','days')
    @api.onchange('supplier_price','customer_price')
    def onchange_supplier_customer_price(self):
        result = {}
        if self.supplier_price and self.room_req and self.days:
            result['supplier_price_total'] = self.supplier_price * self.room_req * self.days
        if self.customer_price and self.room_req and self.days:
            result['customer_price_total'] = self.customer_price * self.room_req * self.days
        return {'value': result}
    
#     def onchange_supplier_customer_price(self, cr, uid, ids, supplier_price,customer_price,room_req,days):
#         result = {}
#         if supplier_price and room_req and days:
#             result['supplier_price_total']=supplier_price * room_req * days
#         if customer_price and room_req and days:
#             result['customer_price_total']=customer_price * room_req * days
#         return {'value': result}
 


class travel_planer_details(models.Model):
    _name = "travel.planer.details"
    _description = "Travel planer details"
    
    
    def get_adult(self):
        """ 
        Gets document number while order in quotation state
        """
        if 'parent_id' in self._context and self._context['parent_id']:
            obj = self.env['custom.tour.itinarary'].browse(self._context['parent_id'])
            if obj:
                return obj.adult
            else:
                return False
    
#     def get_adult(self, cr, uid, context=None):
#         """ 
#         Gets document number while order in quotation state
#         """
#         if context.has_key('parent_id') and context['parent_id']:
#             obj = self.pool.get('custom.tour.itinarary').browse(cr,uid,context['parent_id'])
#             if obj:
#                 return obj.adult
#             else:
#                 return False
            
    
    def get_child(self):
        """ 
        Gets document number while order in quotation state
        """
        if 'parent_id' in self._context and self._context['parent_id']:
            obj = self.env['custom.tour.itinarary'].browse(self._context['parent_id'])
            if obj:
                return obj.child
            else:
                return False
    
#     def get_child(self, cr, uid, context=None):
#         """ 
#         Gets document number while order in quotation state
#         """
#         if context.has_key('parent_id') and context['parent_id']:
#             obj = self.pool.get('custom.tour.itinarary').browse(cr,uid,context['parent_id'])
#             if obj:
#                 return obj.child
#             else:
#                 return False
    
    
    
    travel_planer_id = fields.Many2one('custom.tour.itinarary',string='Itinerary Ref',required=True)
    name = fields.Char("Sequence",size=3,required=True)
    transport_id = fields.Many2one('transport.information',"Transport Company",required=True)
    current_date = fields.Date("Booking Date",required=True)
    transport_type_id = fields.Many2one('product.product','Transport Type',required=True)
    transport_carrier_id = fields.Many2one('transport.carrier','Carrier Name',required=True)
    cost_price = fields.Float("Cost Price(Adult)")
    sale_price = fields.Float("Sale Price(Adult)")
    cost_price_child = fields.Float("Cost Price(Child)")
    sale_price_child = fields.Float("Sale Price(Child)")
    child = fields.Integer("No. of Child",required=True,default=lambda self: self.get_child())
    adult = fields.Integer("No. of Adult",required=True,default=lambda self: self.get_adult())
    price_total_adult = fields.Float("Total Cost Price (Adult)")
    price_total_child = fields.Float("Total Cost Price (Child)")
    price_total_adult_sale = fields.Float("Total Sale Price (Adult)")
    price_total_child_sale = fields.Float("Total Sale Price (Child)")
    from_destination_id = fields.Many2one('tour.destinations','From',required=True)
    to_destination_id = fields.Many2one('tour.destinations','To',required=True)
    travel_class_id = fields.Many2one('travel.class','Travel Class',required=True)
    sale_tax_ids = fields.Many2many('account.tax', 'sale_travel_tax_line_rel', 'tour_itinary_id', 'tax_id', string='Sale Taxes')
    pur_tax_ids = fields.Many2many('account.tax', 'pur_travel_tax_line_rel', 'tour_itinary_id', 'tax_id', strinh = 'Purchase Taxes')
    purches_bol = fields.Boolean('Show Purchase Tax')
    
    
#     _defaults = {
#         'adult': lambda self,cr,uid,ctx: self.get_adult(cr, uid, ctx),
#         'child': lambda self,cr,uid,ctx: self.get_child(cr, uid, ctx),
#     }
    
    @api.depends('transport_type_id')
    @api.onchange('purches_bol')
    def on_change_purchase_bool(self):
        result = {}
        if self.transport_type_id and self.purches_bol:
            product_browse = self.transport_type_id
            result['pur_tax_ids'] = self.env['account.fiscal.position'].map_tax(product_browse.supplier_taxes_id)
        if self.transport_type_id and (not self.purches_bol):
            result['pur_tax_ids'] = []
        return {'value': result}
    
#     def on_change_purchase_bool(self, cr, uid, ids, purches_bol, transport_type_id):
#         result = {}
#         if transport_type_id and purches_bol:
#             product_browse = self.pool.get('product.product').browse(cr,uid,transport_type_id)
#             fpos = False
#             result['pur_tax_ids'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_browse.supplier_taxes_id)
#         if transport_type_id and (not purches_bol):
#             result['pur_tax_ids'] = []
#         return {'value': result}
    
    @api.depends('adult','child','travel_planer_id.pricelist_id')
    @api.onchange('transport_id', 'current_date', 'transport_carrier_id', 'transport_type_id', "travel_class_id", 'from_destination_id', 'to_destination_id')
    def on_change_transport_details(self):
        result = {}
        warning = {}
        if not self.travel_planer_id.pricelist_id:
            raise Warning("PriceList is not Selected for Itinerary!")
        if self.transport_type_id:
            product_browse = self.transport_type_id
            result['sale_tax_ids'] = self.env['account.fiscal.position'].map_tax(product_browse.taxes_id)
        if (self.transport_id and self.current_date and self.transport_carrier_id and self.transport_type_id and self.travel_class_id and self.from_destination_id and self.to_destination_id):
            if self.transport_id.transport_type_info_ids:
                result['cost_price'] = 0.00
                result['sale_price'] = 0.00
                result['cost_price_child'] = 0.00
                result['sale_price_child'] = 0.00
                for line in self.transport_id.transport_type_info_ids:
                    if (line.from_date <= self.current_date and self.current_date <= line.to_date and line.transport_carrier_id.id == self.transport_carrier_id.id and
                        line.transport_type_id.id == self.transport_type_id.id and line.travel_class_id.id == self.travel_class_id.id and 
                        line.from_destination_id.id == self.from_destination_id.id and line.to_destination_id.id == self.to_destination_id.id):
                        adult_total = line.cost_price * self.adult
                        child_total = line.cost_price_child * self.child
                        adult_total_sales = line.sale_price * self.adult
                        child_total_sales = line.sale_price_child * self.child
                        result['cost_price'] = get_price(self, self.travel_planer_id.pricelist_id.id, line.cost_price)
                        result['sale_price'] = get_price(self, self.travel_planer_id.pricelist_id.id, line.sale_price)
                        result['cost_price_child'] = get_price(self, self.travel_planer_id.pricelist_id.id, line.cost_price_child)
                        result['sale_price_child'] = get_price(self, self.travel_planer_id.pricelist_id.id, line.sale_price_child)
                        result['price_total_adult'] = get_price(self,self.travel_planer_id.pricelist_id.id, adult_total)
                        result['price_total_child'] = get_price(self,self.travel_planer_id.pricelist_id.id, child_total)
                        result['price_total_adult_sale'] = get_price(self,self.travel_planer_id.pricelist_id.id, adult_total_sales)
                        result['price_total_child_sale'] = get_price(self,self.travel_planer_id.pricelist_id.id, child_total_sales)
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
        return {'value': result,'warning': warning }
    
    
#     def on_change_transport_details(self, cr, uid, ids, transport_id, current_date, transport_carrier_id, transport_type_id, travel_class_id, from_destination_id, to_destination_id,adult,child,pricelist):
#         result = {}
#         warning = {}
#         if not pricelist:
#             raise osv.except_osv(_("Warning"),_("PriceList is not Selected !"))
#         pricelist_obj=self.pool.get('product.pricelist').browse(cr,uid,pricelist)
#         if transport_type_id:
#             product_browse = self.pool.get('product.product').browse(cr,uid,transport_type_id)
#             fpos = False
#             result['sale_tax_ids'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_browse.taxes_id)
#         if (transport_id and current_date and transport_carrier_id and transport_type_id and travel_class_id and from_destination_id and to_destination_id):
#             res = self.pool.get('transport.information').browse(cr, uid, transport_id)
#             print res,"res.transport_type_info_ids"
#             if res.transport_type_info_ids:
#                 result['cost_price'] = 0.00
#                 result['sale_price'] = 0.00
#                 result['cost_price_child'] = 0.00
#                 result['sale_price_child'] = 0.00
#                 for line in res.transport_type_info_ids:
#                     if (line.from_date <= current_date and current_date <= line.to_date and line.transport_carrier_id.id == transport_carrier_id and
#                          line.transport_type_id.id == transport_type_id and line.travel_class_id.id == travel_class_id and 
#                          line.from_destination_id.id == from_destination_id and line.to_destination_id.id == to_destination_id):
#                         adult_total = line.cost_price * adult
#                         child_total = line.cost_price_child * child
#                         adult_total_sales = line.sale_price * adult
#                         child_total_sales = line.sale_price_child * child
#                         result['cost_price'] = get_price(self, cr, uid, ids, pricelist, line.cost_price)
#                         result['sale_price'] = get_price(self, cr, uid, ids, pricelist, line.sale_price)
#                         result['cost_price_child'] = get_price(self, cr, uid, ids, pricelist, line.cost_price_child)
#                         result['sale_price_child'] = get_price(self, cr, uid, ids, pricelist, line.sale_price_child)
#                         result['price_total_adult'] = get_price(self, cr, uid, ids, pricelist, adult_total)
#                         result['price_total_child'] = get_price(self, cr, uid, ids, pricelist, child_total)
#                         result['price_total_adult_sale'] = get_price(self, cr, uid, ids, pricelist, adult_total_sales)
#                         result['price_total_child_sale'] = get_price(self, cr, uid, ids, pricelist, child_total_sales)
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
#         return {'value': result,'warning': warning }
    
    
    @api.onchange('adult', 'child', 'cost_price', 'sale_price', 'cost_price_child', 'sale_price_child')
    def on_change_adult_child_pre_setting(self):
        result = {}
        result['price_total_adult'] = self.cost_price * self.adult
        result['price_total_child'] = self.cost_price_child * self.child
        result['price_total_adult_sale'] = self.sale_price * self.adult
        result['price_total_child_sale'] = self.sale_price_child * self.child
        return {'value': result}
    
#     def on_change_adult_child_pre_setting(self, cr, uid, ids, adult, child, cost_price, sale_price, cost_price_child, sale_price_child):
#         result = {}
#         result['price_total_adult'] = cost_price * adult
#         result['price_total_child'] = cost_price_child * child
#         result['price_total_adult_sale'] = sale_price * adult
#         result['price_total_child_sale'] = sale_price_child * child
#         return {'value': result}
    



class tour_days(models.Model):
    _name = "tour.days"
    _description = "Tour Days"
    _rec_name = "name"

    name = fields.Char('Name',size=16,required=True)
              



class custom_tour_programme(models.Model):
    _name = "custom.tour.programme"
    _description = "Custom Tour Programme"
    
    
    @api.model
    def create(self,vals): 
        # function overwrites create method and auto generate request no. 
        so = super(custom_tour_programme, self).create(vals)
        if vals.get('sites_ids'):
            desc = ''
            for sites in vals['sites_ids'][0][2]:
                res = self.env['product.product'].browse(sites)
                sale_tax_ids = self.env['account.fiscal.position'].map_tax(res.taxes_id)
                pur_tax_ids = self.env['account.fiscal.position'].map_tax(res.supplier_taxes_id)
                site_costing = self.env['sites.costing.line'].create({'itinary_id': vals['program_id'],'name':sites , 'new_cost_price':res.product_tmpl_id.standard_price,'new_sale_price':res.product_tmpl_id.list_price,'sale_tax_ids':[(6,0,[i.id for i in sale_tax_ids])],'pur_tax_ids':[(6,0,[i.id for i in pur_tax_ids])],'tour_program_id':so.id})
                so.write({'sites_costing_ids':[(4,site_costing.id)]})
                desc += res.name + ', '
            so.write({'description':desc})
            
        return so
    
#     def create(self, cr, uid, vals, context=None): 
#         # function overwrites create method and auto generate request no. 
#         so = super(custom_tour_programme, self).create(cr, uid, vals, context=context)
#         if vals['sites_ids']:
#             desc = ''
#             for sites in vals['sites_ids'][0][2]:
#                 res = self.pool.get('product.product').browse(cr, uid, sites)
#                 fpos = False
#                 sale_tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, res.taxes_id)
#                 pur_tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, res.supplier_taxes_id)
# #                 site_costing = self.pool.get('sites.costing.line').create(cr, uid, {'itinary_id': vals['program_id'],'name':sites ,'sale_tax_ids':[(6,0,sale_tax_ids)],'pur_tax_ids':[(6,0,pur_tax_ids)],'tour_program_id':so})
#                 site_costing = self.pool.get('sites.costing.line').create(cr, uid, {'itinary_id': vals['program_id'],'name':sites , 'new_cost_price':res.product_tmpl_id.standard_price,'new_sale_price':res.product_tmpl_id.list_price,'sale_tax_ids':[(6,0,sale_tax_ids)],'pur_tax_ids':[(6,0,pur_tax_ids)],'tour_program_id':so})
#                 desc += res.name + ', '
#             self.write(cr, uid, [so], {'description':desc})
#             
#         return so
    
    @api.multi
    def write(self, vals):
        """
        Overriding the write method
        """
        for obj in self:
            len_sites = len(obj.sites_ids)
            if 'sites_ids' in vals and vals['sites_ids'] : 
                len_new_sites = len(vals['sites_ids'][0][2])
                desc = obj.description or ''
                if len_new_sites > len_sites:
                    add_site = len_new_sites - len_sites
                    new_list = vals['sites_ids'][0][2][len_sites:len_new_sites]
                    for sites in new_list:
                        res = self.env['product.product'].browse(sites)
                        sale_tax_ids = self.env['account.fiscal.position'].map_tax(res.taxes_id)
                        pur_tax_ids = self.env['account.fiscal.position'].map_tax(res.supplier_taxes_id)
                        site_id = self.env['sites.costing.line'].create({'itinary_id': obj.program_id.id, 
                                                                         'name':sites ,
                                                                         'new_cost_price':res.product_tmpl_id.standard_price,
                                                                         'new_sale_price':res.product_tmpl_id.list_price,
                                                                         'sale_tax_ids':[(6,0,sale_tax_ids)],
                                                                         'pur_tax_ids':[(6,0,pur_tax_ids)],
                                                                         'tour_program_id':obj.id})
                        desc += res.name + ', '
                    vals.update({'description': desc })
                else:
                    orignal_list = [] 
                    for site in obj.sites_ids: 
                        orignal_list.append(site.id)
                    updated_list = []
                    for i in orignal_list:
                        temp=True
                        for j in vals['sites_ids'][0][2]:
                            if i==j:
                                temp=False
                        if temp == True:
                            updated_list.append(i);
                    for sites in updated_list:
                        site_costing = self.env['sites.costing.line'].search([('itinary_id', '=', obj.program_id.id),('tour_program_id', '=', obj.id),('name.id', '=', sites)])
                        if site_costing:
                            res = self.env['product.product'].browse(sites)
                            str_remove = res.name + ', '
                            desc = desc.replace(str_remove,"")
                            vals.update({'description': desc })
                            site_unlink = site_costing.unlink()
        return super(custom_tour_programme, self).write(vals)
    
    
#     def write(self, cr, uid, ids, vals, context=None):
#         """
#         Overriding the write method
#         """
#         for obj in self.browse(cr, uid, ids):
#             len_sites = len(obj.sites_ids)
#             if vals.has_key('sites_ids') and vals['sites_ids'] : 
#                 len_new_sites = len(vals['sites_ids'][0][2])
#                 desc = obj.description or ''
#                 if len_new_sites > len_sites:
#                     add_site = len_new_sites - len_sites
#                     new_list = vals['sites_ids'][0][2][len_sites:len_new_sites]
#                     for sites in new_list:
#                         res = self.pool.get('product.product').browse(cr, uid, sites)
#                         fpos = False
#                         sale_tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, res.taxes_id)
#                         pur_tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, res.supplier_taxes_id)
# #                         site_id = self.pool.get('sites.costing.line').create(cr, uid, {'itinary_id': obj.program_id.id, 'name':sites ,'sale_tax_ids':[(6,0,sale_tax_ids)],'pur_tax_ids':[(6,0,pur_tax_ids)],'tour_program_id':obj.id})
#                         site_id = self.pool.get('sites.costing.line').create(cr, uid, {'itinary_id': obj.program_id.id, 'name':sites ,'new_cost_price':res.product_tmpl_id.standard_price,'new_sale_price':res.product_tmpl_id.list_price,'sale_tax_ids':[(6,0,sale_tax_ids)],'pur_tax_ids':[(6,0,pur_tax_ids)],'tour_program_id':obj.id})
#                         desc += res.name + ', '
#                     vals.update({'description': desc })
#                 else:
#                     orignal_list = [] 
#                     for site in obj.sites_ids: 
#                         orignal_list.append(site.id)
#                     updated_list = []
#                     for i in orignal_list:
#                         temp=True
#                         for j in vals['sites_ids'][0][2]:
#                             if i==j:
#                                 temp=False
#                         if temp == True:
#                             updated_list.append(i);
#                     for sites in updated_list:
#                         site_costing = self.pool.get('sites.costing.line').search(cr, uid, [('itinary_id', '=', obj.program_id.id),('tour_program_id', '=', obj.id),('name.id', '=', sites)])
#                         if site_costing:
#                             res = self.pool.get('product.product').browse(cr, uid, sites)
#                             str_remove = res.name + ', '
#                             desc = desc.replace(str_remove,"")
#                             vals.update({'description': desc })
#                             site_unlink = self.pool.get('sites.costing.line').unlink(cr, uid,site_costing)
#         return super(custom_tour_programme, self).write(cr, uid, ids, vals, context=context)   
    

    name = fields.Many2one('tour.days','Days',required=True)
    description = fields.Text('Description')
    breakfast = fields.Boolean('Breakfast')
    lunch = fields.Boolean('Lunch')
    dinner = fields.Boolean('Dinner')
    program_id = fields.Many2one('custom.tour.itinarary','Itinerary Id')
    sites_ids = fields.Many2many('product.product','program_sites_rel', 'program_ids', 'sites_id',string='Sites Name',domain=[('type','=','service'),('categ_id','=',8)])
              
    
    
    def unlink(self):
        """
        Allows to delete Product Category which are not defined in demo data
        """
        for rec in self:
            desc = rec.description or ''
            for sites in rec.sites_ids:
                site_costing = self.env['sites.costing.line'].search([('itinary_id', '=', rec.program_id.id),('tour_program_id', '=', rec.id),('name.id', '=', sites.id)])
                if site_costing:
                    res = sites
                    str_remove = sites.name + ', '
                    desc = desc.replace(str_remove,"")
                    site_unlink = site_costing.unlink()
            rec.write({'description':desc})
        return super(custom_tour_programme, self).unlink()
    
#     def unlink(self, cr, uid, ids, context):
#         """
#         Allows to delete Product Category which are not defined in demo data
#         """
#         for rec in self.browse(cr, uid, ids, context = context):
#             desc = rec.description or ''
#             for sites in rec.sites_ids:
#                 site_costing = self.pool.get('sites.costing.line').search(cr, uid, [('itinary_id', '=', rec.program_id.id),('tour_program_id', '=', rec.id),('name.id', '=', sites.id)])
#                 if site_costing:
#                     res = self.pool.get('product.product').browse(cr, uid, sites)
#                     str_remove = sites.name + ', '
#                     desc = desc.replace(str_remove,"")
# #                    vals.update({'description': description })
#                     site_unlink = self.pool.get('sites.costing.line').unlink(cr, uid,site_costing)
#             self.write(cr, uid, [rec.id], {'description':desc})
#         return super(custom_tour_programme, self).unlink(cr, uid, ids, context = context)
              



class visa_costing_line(models.Model):
    _name = "visa.costing.line"
    _description = "Visa costing Lines"

    @api.depends('sale_price','cost_price')
    def _get_total_visa_amt(self):
      
        # cost_price = sale_price = total_cost_price = total_sale_price = 0.00
        
        for obj in self:
            visa_cost = []
            if obj.visa_type == 'single':
                self._cr.execute("""select service_cost,cost_price from visa_scheme where name='Tourist Visa(Single Entry)'""")                        
                visa_cost = self._cr.fetchone()
                if not visa_cost:
                    raise UserError('Costing is missing For Visa')
            else:
                self._cr.execute("""select service_cost,cost_price from visa_scheme where name='Tourist Visa(Multiple Entry)'""")                        
                visa_cost = self._cr.fetchone()
                if not visa_cost:
                    raise UserError('Costing is missing For Visa')
            total_cost = visa_cost[1] * obj.itinary_id.total_seat
            total_sale = visa_cost[0] * obj.itinary_id.total_seat



            obj.cost_price = get_price(self, obj.itinary_id.pricelist_id.id, visa_cost[1])
            obj.sale_price = get_price(self,  obj.itinary_id.pricelist_id.id, visa_cost[0])
            obj.total_cost_price = get_price(self,  obj.itinary_id.pricelist_id.id, total_cost)
            obj.total_sale_price = get_price(self, obj.itinary_id.pricelist_id.id, total_sale)

            
        #     record = {
        #         'cost_price':cost_price,
        #         'sale_price':sale_price,
        #         'total_cost_price':total_cost_price,
        #         'total_sale_price':total_sale_price,
        #     }
        #     res[obj.id] = record
        # return res
    
#     def _get_total_visa_amt(self,cr,uid,ids,args1,args2,context=None):
#         res = {}
#         cost_price = sale_price = total_cost_price = total_sale_price = 0.00
#         
#         for obj in self.browse(cr,uid,ids):
#             visa_cost = []
#             if obj.visa_type == 'single':
#                 cr.execute("""select service_cost,cost_price from visa_scheme where name='Tourist Visa(Single Entry)'""")                        
#                 visa_cost = cr.fetchone()
#                 if not visa_cost:
#                     raise osv.except_osv(_('Error !'), _('Costing is missing For Visa'))
#                 print "Scheme",visa_cost
#             else:
#                 cr.execute("""select service_cost,cost_price from visa_scheme where name='Tourist Visa(Multiple Entry)'""")                        
#                 visa_cost = cr.fetchone()
#                 if not visa_cost:
#                     raise osv.except_osv(_('Error !'), _('Costing is missing For Visa'))
#                 print "Scheme",visa_cost
#             total_cost = visa_cost[1] * obj.itinary_id.total_seat
#             total_sale = visa_cost[0] * obj.itinary_id.total_seat
# 
#             cost_price = get_price(self, cr, uid, ids, obj.itinary_id.pricelist_id.id, visa_cost[1])
#             sale_price = get_price(self, cr, uid, ids, obj.itinary_id.pricelist_id.id, visa_cost[0])
#             total_cost_price = get_price(self, cr, uid, ids, obj.itinary_id.pricelist_id.id, total_cost)
#             total_sale_price = get_price(self, cr, uid, ids, obj.itinary_id.pricelist_id.id, total_sale)
#             
#             
#             record = {
#                 'cost_price':cost_price,
#                 'sale_price':sale_price,
#                 'total_cost_price':total_cost_price,cost_price
#                 'total_sale_price':total_sale_price,
#             }
#             res[obj.id] = record
#         return res

    itinary_id = fields.Many2one('custom.tour.itinarary', 'Itinerary Ref')
    name = fields.Many2one('product.product', 'Visa', required=True)
    country_id = fields.Many2one('res.country', 'Country', required=True)
    visa_type = fields.Selection(
        [('single', 'Tourist Visa(Single Entry)'), ('multiple', 'Tourist Visa(Multiple Entry)')], "Visa Type")
    total_person = fields.Integer('No. of Person', required=True)
    cost_price = fields.Float(compute=_get_total_visa_amt, store=True, multi='dc', string='Visa Cost Price',
                              digits=dp.get_precision('Account'))
    sale_price = fields.Float(compute=_get_total_visa_amt, store=True, multi='dc', string='Visa Sale Price',
                              digits=dp.get_precision('Account'))
    total_cost_price = fields.Float(compute=_get_total_visa_amt, store=True, multi='dc', string='Total Cost Price',
                                    digits=dp.get_precision('Account'))
    total_sale_price = fields.Float(compute=_get_total_visa_amt, store=True, multi='dc', string='Total Sale Price',
                                    digits=dp.get_precision('Account'))
    sale_tax_ids = fields.Many2many('account.tax', 'sale_visa_tax_line_rel', 'tour_itinary_id', 'tax_id',
                                    string='Sale Taxes')
    pur_tax_ids = fields.Many2many('account.tax', 'pur_visa_tax_line_rel', 'tour_itinary_id', 'tax_id',
                                   string='Purchase Taxes')
    destination_id = fields.Many2one('tour.destination.line', string='Tour destination Ref')





class tour_service_line_details(models.Model):
    _name='tour.service.line.details'
    _description='tour Itinarary Service line details'
    
    @api.depends('sale_price')
    def _amount_line(self):
        for line in self:
            price = line.sale_price * (1 - (line.discount or 0.0) / 100.0)
            line.price_subtotal = price * line.product_uom_qty




    
#     def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
#         tax_obj = self.pool.get('account.tax')
#         cur_obj = self.pool.get('res.currency')
#         user_id = self.pool.get('res.users').browse(cr,uid,uid)
#         res = {}
#         if context is None:
#             context = {}
#         for line in self.browse(cr, uid, ids, context=context):
#             price = line.sale_price * (1 - (line.discount or 0.0) / 100.0)
#             price_subtotal = price * line.product_uom_qty
#             res[line.id]=price_subtotal
#         return res
    
    @api.depends('price_unit')
    def _amount_line_cost(self):
        for line in self:
            line.price_subtotal_cost = line.price_unit * line.product_uom_qty



    
#     def _amount_line_cost(self, cr, uid, ids, field_name, arg, context=None):
#         tax_obj = self.pool.get('account.tax')
#         cur_obj = self.pool.get('res.currency')
#         user_id = self.pool.get('res.users').browse(cr,uid,uid)
#         res = {}
#         if context is None:
#             context = {}
#         for line in self.browse(cr, uid, ids, context=context):
#             price = line.price_unit
#             price_subtotal_cost = price * line.product_uom_qty
#             res[line.id]=price_subtotal_cost
#         return res
    
    
    @api.depends('itinarary_id.pricelist_id')
    @api.onchange('product_id')
    def on_change_product_id(self):
        result = {}
        if not self.itinarary_id.pricelist_id:
            raise Warning("PriceList is not Selected !")
        if self.product_id:
            result['pur_tax_ids'] = self.env['account.fiscal.position'].map_tax(self.product_id.supplier_taxes_id)
            result['price_unit'] = get_price(self, self.itinarary_id.pricelist_id.id, self.product_id.standard_price)
            result['sale_price'] = get_price(self, self.itinarary_id.pricelist_id.id, self.product_id.list_price)
            result['product_uom'] = self.product_id.uom_id.id
        return {'value': result}
    
#     def on_change_product_id(self, cr, uid, ids, product_id,pricelist):
#         result = {}
#         if not pricelist:
#             raise osv.except_osv(_("Warning"),_("PriceList is not Selected !"))
#         if product_id:
#             pricelist_obj=self.pool.get('product.pricelist').browse(cr,uid,pricelist)
#             print "on_change_product_id",product_id
#             product_browse = self.pool.get('product.product').browse(cr,uid,product_id)
#             print product_browse,"product_browse===============",product_browse.taxes_id
#             fpos = False
#             result['pur_tax_ids'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_browse.supplier_taxes_id)
#             result['price_unit'] = get_price(self, cr, uid, ids, pricelist, product_browse.standard_price)
#             result['sale_price'] = get_price(self, cr, uid, ids, pricelist, product_browse.list_price)
#             result['product_uom'] = product_browse.uom_id.id
#         print result,"result"
#         return {'value': result}
    
    
    @api.depends('product_id')
    @api.onchange('purches_bol')
    def on_change_purchase_bool(self):
        result = {}
        if self.product_id and self.purches_bol:
            result['pur_tax_ids'] = self.env['account.fiscal.position'].map_tax(self.product_id.supplier_taxes_id)
        if self.product_id and (not self.purches_bol):
            result['pur_tax_ids'] = []
        return {'value': result}
    
    
#     def on_change_purchase_bool(self, cr, uid, ids, purches_bol, product_id):
#         result = {}
#         if product_id and purches_bol:
#             print "on_change_product_id",product_id
#             product_browse = self.pool.get('product.product').browse(cr,uid,product_id)
#             fpos = False
#             result['pur_tax_ids'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_browse.supplier_taxes_id)
#         if product_id and (not purches_bol):
#             result['pur_tax_ids'] = []
#         print result,"result"
#         return {'value': result}
    
    
    
    product_id = fields.Many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], change_default=True,required=True)
    price_unit = fields.Float('Cost Price', required=True, digits= dp.get_precision('Cost Price'),default=0.0)
    sale_price = fields.Float('Sale Price', required=True, digits= dp.get_precision('Sale Price'))
    product_uom_qty = fields.Float('Quantity (UoM)', digits=(16, 2), required=True,default=1)
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure ', required=True)
    price_subtotal = fields.Float(compute=_amount_line, string='Sale Subtotal', digits= dp.get_precision('Sale Price'))
    price_subtotal_cost = fields.Float(compute=_amount_line_cost, string='Cost Subtotal', digits= dp.get_precision('Cost Price'))
    discount = fields.Float('Discount (%)', digits=(16, 2),default=0.0)
    sale_tax_ids = fields.Many2many('account.tax', 'sale_service_tax_line_rel1', 'tour_itinary_new_id1', 'tax_new_id1', 'Sale Taxes')
    pur_tax_ids = fields.Many2many('account.tax', 'pur_service_tax_line_rel2', 'tour_itinary_new_id2', 'tax_new_id2', 'Purchase Taxes')
    itinarary_id = fields.Many2one('custom.tour.itinarary','itinarary_id',ondelete='cascade')
    purches_bol = fields.Boolean('Show Purchase Tax')
    
    
    
#     _defaults = {
#         'discount': 0.0,
#         'product_uom_qty': 1,
#         'price_unit': 0.0,
#     }




class itinerary_lead_history(models.Model):
    _name='itinerary.lead.history'
    _description='itinerary lead history'
    
    ref_id = fields.Many2one('crm.lead','History',required=True)
    name = fields.Char("Itinerary No.",size=128,readonly=True)
    contact_name = fields.Char('Contact Name',size=64,readonly=True)
    current_date = fields.Date("Creation Date",required=True,)
    update_date = fields.Date("Last Updated Date",required=True,)
    state = fields.Selection([
                             ('draft', 'Draft'),
                             ('confirm', 'Confirm'),
                             ('send_to', 'Send To Customer'),
                             ('approve', 'Approved'),
                             ('refused', 'Refused'),
                             ], 'Status',readonly=True)




class tour_destinations(models.Model):
    _inherit = "tour.destinations"
    _description = "Tour Destinations"
    
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        ids = super(tour_destinations, self).search(args, offset, limit, order, count=count)
        if 'tour_desti_parent_id' in self._context and self._context['tour_desti_parent_id']:
            main_obj = self.env['custom.tour.itinarary'].search([('name','=', self._context['tour_desti_parent_id'])],False, False, False)
            new_ids = []
            for dest_line in main_obj.tour_destination_ids:
                new_ids.append(dest_line.destination_id.id)
            
            return new_ids
        return ids
    
#     def search(self, cr, uid, args, offset=0, limit=None, order=None, context={}, count=False):
#         ids = super(tour_destinations, self).search(cr, uid, args, offset, limit, order, context=context, count=count)
#         print "context",context
#         if context.has_key('tour_desti_parent_id') and context['tour_desti_parent_id']:
#             main_obj_ids = self.pool.get('custom.tour.itinarary').search(cr,uid,[('name','=', context['tour_desti_parent_id'])],False, False, False, context)
#             main_obj = self.pool.get('custom.tour.itinarary').browse(cr,uid,main_obj_ids[0])
#             new_ids = []
#             for dest_line in main_obj.tour_destination_ids:
#                 new_ids.append(dest_line.destination_id.id)
#             
#             return new_ids
#         return ids
            


class crm_lead(models.Model):
    """ CRM Lead Case """
    _inherit = "crm.lead"
   
    _description = "Lead/Opportunity"
   
    itinarary_ids = fields.One2many('itinerary.lead.history','ref_id','Itinerary History')
    
    
    
    def convert_partner(self, action='create', partner_id=False):
        """
        This function convert partner based on action.
        if action is 'create', create new partner with contact and assign lead to new partner_id.
        otherwise assign lead to specified partner_id
        """
        """ Commit by Anup, the partner condition because when customer create new partner to lead and     
        after change the exist type to create type then the condtion is true by which it create the partner for lead accoding to existance partner """ 

        if self._context is None:
            self._context = {}
        partner_ids = {}
        for lead in self:
            if action == 'create':
                partner_id = self._lead_create_partner(lead)
                self._lead_create_partner_address(lead, partner_id)
            self._lead_set_partner(lead, partner_id)
            partner_ids[lead.id] = partner_id.id
        return partner_ids
    
#     def convert_partner(self, cr, uid, ids, action='create', partner_id=False, context=None):
#         """
#         This function convert partner based on action.
#         if action is 'create', create new partner with contact and assign lead to new partner_id.
#         otherwise assign lead to specified partner_id
#         """
#         """ Commit by Anup, the partner condition because when customer create new partner to lead and     
#         after change the exist type to create type then the condtion is true by which it create the partner for lead accoding to existance partner """ 
# 
#         if context is None:
#             context = {}
#         partner_ids = {}
#         for lead in self.browse(cr, uid, ids, context=context):
#             if action == 'create':
#                 partner_id = self._lead_create_partner(cr, uid, lead, context=context)
#                 self._lead_create_partner_address(cr, uid, lead, partner_id, context=context)
#             self._lead_set_partner(cr, uid, lead, partner_id, context=context)
#             partner_ids[lead.id] = partner_id
#         return partner_ids
    
