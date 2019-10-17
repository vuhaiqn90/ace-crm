from odoo import fields, models, api


    
class tour_booking_cancellation(models.Model):
    _name = 'tour.booking.cancellation'
    _description ='Tour booking cancellation'
    
    
    tour_id = fields.Many2one("tour.booking","Tour ID")
    tour_dates_id = fields.Many2one('tour.dates',"Tour Dates",readonly=True)
    current_date = fields.Date("Booking Date",readonly=True)
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist',readonly=True)
    tour_customer_ids = fields.One2many('tour.customer.details','tour_book_id','Tour Customer Details')
    
    
    @api.onchange('tour_id')
    def on_change_tour_id(self):
        result = {}
        trans_obj = self.tour_id
        result['tour_dates_id'] = trans_obj.tour_dates_id.id
        result['current_date'] = trans_obj.current_date
        result['pricelist_id'] = trans_obj.pricelist_id.id
        id_list = []
        for customer in trans_obj.tour_customer_ids:
            id_list.append(customer.id)
        result['tour_customer_ids'] = id_list
        return {'value': result}
    
#     def on_change_tour_id(self,cr,uid,ids,tour_id):
#         result = {}
#         trans_obj = self.pool.get('tour.booking').browse(cr,uid,tour_id)
#         result['tour_dates_id'] = trans_obj.tour_dates_id.id
#         result['current_date'] = trans_obj.current_date
#         result['pricelist_id'] = trans_obj.pricelist_id.id
#         id_list = []
#         for customer in trans_obj.tour_customer_ids:
#             id_list.append(customer.id)
#         result['tour_customer_ids'] = id_list
#         return {'value': result}
    
    
    def print_report(self):
        data = {}
        if self._context is None:
            context = {}
        data['form'] = self.read(['start_date','end_date','categ_id','report_basis','partner_id'])[0]
        data['ids'] = self._context.get('active_ids', [])
        data['model'] = self._context.get('active_model', 'ir.ui.menu')
        if data['form']['start_date'] > data['form']['end_date']:
            raise Warning('Please Check the start and end date !!')
        
        return {
           'type': 'ir.actions.report.xml',
           'report_name': 'lead.report.by.agent',
           'datas': data,
           } 
    
#     def print_report(self, cr, uid, ids, context=None):
#         data = {}
#         print context,"context"
#         print ids,"ids"
#         if context is None:
#             context = {}
#         data['form'] = self.read(cr, uid, ids, ['start_date','end_date','categ_id','report_basis','partner_id'])[0]
#         data['ids'] = context.get('active_ids', [])
#         data['model'] = context.get('active_model', 'ir.ui.menu')
#         if data['form']['start_date'] > data['form']['end_date']:
#             raise osv.except_osv(('warning'),('Please Check the start and end date !!'))
#         
#         return {
#            'type': 'ir.actions.report.xml',
#            'report_name': 'lead.report.by.agent',
#            'datas': data,
#            } 
             
