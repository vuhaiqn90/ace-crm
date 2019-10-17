from odoo import fields, models, api
from odoo.tools.translate import _
from datetime import datetime,timedelta
from odoo.exceptions import UserError


    
class refund_payment_entry_wizard(models.TransientModel):
    _name = 'refund_payment_journal_entry.wizard'
    _description ='refund_payment_journal_entry Detail Wizard'
    
    name = fields.Char('Description',size=100,readonly=True,default=lambda *a: 'Tour Cancellation Journal Entry')
    cancellation_id = fields.Many2one('tour.cancellation',"Tour Cancellation ID",readonly=True,default=lambda self: self._get_default_rec())
    partner_id = fields.Many2one('res.partner',"Customer",readonly=True,default=lambda self: self._get_default_partner_val())
    payment_date = fields.Date('Payment Date',required=True)
    journal_id = fields.Many2one('account.journal',"Journal",required=True)
    booking_charge = fields.Float('Booking Charges',readonly=True,default=lambda self: self._get_default_val()[0])
    deduct_amt = fields.Float('Deducted Ammount',readonly=True,default=lambda self: self._get_default_val()[1])
    refund_amt = fields.Float('Refund Ammount',readonly=True,default=lambda self: self._get_default_val()[2])
    
    
    def allow_to_send(self):
        for obj in self:
            if obj.cancellation_id.tour_booking_invoice_ids.state != 'paid':
                print("obj.cancellation_id.tour_booking_invoice_ids.state",obj.cancellation_id.tour_booking_invoice_ids)
                raise UserError("Invoice Is Not Paid Yet. Please Pay The Invoice Amount")
            if not obj.cancellation_id.tour_id.product_id.property_account_expense_id:
                raise UserError("Account is not set for selected service."+obj.cancellation_id.tour_id.product_id.name)
            
            move_id = self.env['account.move'].create({
                                                            'journal_id': obj.journal_id.id,
                                                            'ref': obj.cancellation_id.name,
                                                            })
            
            move_line1 = {
                          'name': obj.name,
                          'move_id': move_id.id,
                          'account_id': obj.cancellation_id.tour_id.product_id.property_account_expense_id.id,
                          'debit': obj.refund_amt,
                          'credit': 0.0,
                          'ref': obj.cancellation_id.name,
                          'journal_id': obj.journal_id.id,
                          'partner_id': obj.partner_id.id,
                          'date': obj.payment_date
                          }
            
            move_line2 = {
                          'name': obj.name,
                          'move_id': move_id.id,
                          'account_id': obj.journal_id.default_credit_account_id.id,
                          'debit':0.0,
                          'credit':  obj.refund_amt,
                          'ref': obj.cancellation_id.name,
                          'journal_id': obj.journal_id.id,
                          'partner_id': obj.partner_id.id,
                          'date': obj.payment_date
                          }
            d = obj.cancellation_id.tour_customer_ids
            changed_ids = []
            for br in d:
                i = br.id
                br.write({'state':'cancel'})
                n = br.partner_id
                changed_ids.append(n)
                
            for tour_booking_customer_ids in obj.cancellation_id.tour.tour_customer_ids :
                if tour_booking_customer_ids.partner_id in changed_ids :
                    tour_booking_customer_ids.write({'state':'cancel'})
            
            move_id.write({'line_ids':[(0,0,move_line1),(0,0,move_line2)], 'state':'posted'})
            avl_seat = obj.cancellation_id.tour_dates_id.available_seat
            avl_seat +=  obj.cancellation_id.adult + obj.cancellation_id.child
            obj.cancellation_id.tour_dates_id.write({'available_seat':avl_seat})
            obj.cancellation_id.write({'state':'done'})
            
        return { 'type':'ir.actions.act_window_close' }
    
#     def allow_to_send(self, cr, uid, ids, context=None):
#         for obj in self.browse(cr,uid,ids):
#             if obj.cancellation_id.tour_booking_invoice_ids.state != 'paid':
#                 raise osv.except_osv(_("Warnning"),_("Invoice Is Not Paid Yet. Please Pay The Invoice Amount"))
#             
#             if not obj.cancellation_id.tour_id.product_id.property_account_expense_id:
#                 raise osv.except_osv(_("Warning"),_("Account is not set for selected service.")+_(obj.cancellation_id.tour_id.product_id.name))
#             
#             move_id = self.pool.get('account.move').create(cr, uid,
#                                                            {
#                                                             'journal_id': obj.journal_id.id,
#                                                             'ref': obj.cancellation_id.name,
#                                                             })
#             
#             move_line1 = {
#                           'name': obj.name,
#                           'move_id': move_id,
#                           'account_id': obj.cancellation_id.tour_id.product_id.property_account_expense_id.id,
#                           'debit': obj.refund_amt,
#                           'credit': 0.0,
#                           'ref': obj.cancellation_id.name,
#                           'journal_id': obj.journal_id.id,
#                           'partner_id': obj.partner_id.id,
#                           'date': obj.payment_date
#                           }
#             
#             move_line2 = {
#                           'name': obj.name,
#                           'move_id': move_id,
#                           'account_id': obj.journal_id.default_credit_account_id.id,
#                           'debit':0.0,
#                           'credit':  obj.refund_amt,
#                           'ref': obj.cancellation_id.name,
#                           'journal_id': obj.journal_id.id,
#                           'partner_id': obj.partner_id.id,
#                           'date': obj.payment_date
#                           }
#             print "mvoe line 1--------->", move_line1
#             print "move ine 2 =========>", move_line2
#             d = obj.cancellation_id.tour_customer_ids
#             changed_ids = []
#             for br in d:
#                 i = br.id
#                 print i,"I==\n"
#                 self.pool.get('tour.customer.details').write(cr, uid, i,{'state':'cancel'})
#                 cobj = self.pool.get('tour.customer.details').browse(cr, uid, i)
#                 n = cobj.partner_id
#                 changed_ids.append(n)
#                 
#             print changed_ids,"FOR===\n"
#             print obj.cancellation_id.tour.tour_customer_ids
#             for tour_booking_customer_ids in obj.cancellation_id.tour.tour_customer_ids :
#                 id1 = tour_booking_customer_ids.id
#                 r_partner_id = self.pool.get('tour.customer.details').browse(cr, uid, id1)
#                 
#                 if r_partner_id.partner_id in changed_ids :
#                     self.pool.get('tour.customer.details').write(cr, uid, id1,{'state':'cancel'})
#             
#             self.pool.get('account.move').write(cr, uid, [move_id], {'line_ids':[(0,0,move_line1),(0,0,move_line2)], 'state':'posted'})
#             avl_seat = self.pool.get('tour.dates').browse(cr, uid, obj.cancellation_id.tour_dates_id.id).available_seat
#             avl_seat +=  obj.cancellation_id.adult + obj.cancellation_id.child
#             self.pool.get('tour.dates').write(cr, uid, obj.cancellation_id.tour_dates_id.id, {'available_seat':avl_seat})
#             self.pool.get('tour.cancellation').write(cr, uid, obj.cancellation_id.id, {'state':'done'})
#             
#         return { 'type':'ir.actions.act_window_close' }
    
    
    def _get_default_rec(self):
        if self._context is None:
            self._context = {}
        if 'ids' in self._context:
            res=self._context['ids']
        return res
    
#     def _get_default_rec(self, cr, uid, context=None):
#         if context is None:
#             context = {}
#         if 'ids' in context:
#             res=context['ids']
#         return res
    
    
    def _get_default_val(self):
        v_list = [0.0,0.0,0.0]
        
        if self._context is None:
            self._context = {}
            
        if 'ids' in self._context:
            coll_obj = self.env['tour.cancellation'].browse(self._context['ids'] )
            t_amt = coll_obj.total_amt
            v_list[0] = t_amt
            c_date = datetime.strptime(str(coll_obj.cancel_date), '%Y-%m-%d').date()
            s_date = datetime.strptime(str(coll_obj.tour_dates_id.start_date), '%Y-%m-%d').date()
            t_days = (s_date - c_date).days + 1
            
            d_policy = self.env['tour.deduction.policy'].search([])
            
            if d_policy :

                for record in d_policy :
                    obj = record
                    perc = obj.deduction_percentage
                    print("obj-------------------",obj)
                    min = obj.name
                    max = obj.max_limit
                    if t_days >= min and t_days <= max :
                        perc = obj.deduction_percentage
                        break
                    print("perc--------------------------------",perc)
                if perc > 0 :
                    deduct_amt = (perc * t_amt)/100
                    v_list[1] = deduct_amt
                    v_list[2] = t_amt - deduct_amt
                    
                else :
                    raise UserError("Please Configure the deduction Policy 112")
                
            else :
                raise UserError("Please Configure the deduction Policy1")
            
        return v_list
    
    
#     def _get_default_val(self, cr, uid, context=None):
#         v_list = [0.0,0.0,0.0]
#         
#         if context is None:
#             context = {}
#             
#         if 'ids' in context:
#             coll_obj = self.pool.get('tour.cancellation').browse(cr, uid,context['ids'] )
#             print coll_obj,"coll_obj====" 
#             t_amt = coll_obj.total_amt
#             v_list[0] = t_amt
#             print coll_obj.cancel_date,type(coll_obj.cancel_date),"coll_obj.current_date-----"
#             print coll_obj.tour_dates_id.start_date, type(coll_obj.tour_dates_id.start_date),"coll_obj.tour_dates_id.name---\n"
#             
#             c_date = mx.DateTime.strptime(coll_obj.cancel_date[0:10], '%Y-%m-%d')
#             s_date = mx.DateTime.strptime(coll_obj.tour_dates_id.start_date[0:10], '%Y-%m-%d')
#             t_days = (s_date - c_date).days + 1
#             
#             d_policy = self.pool.get('tour.deduction.policy').search(cr, uid,[])
#             
#             if d_policy :
#                 perc = 0.0
#                 for record in d_policy :
#                     obj = self.pool.get('tour.deduction.policy').browse(cr, uid,record)
#                     min = obj.name
#                     max = obj.max_limit
#                     if t_days >= min and t_days <= max :
#                         perc = obj.deduction_percentage
#                         break
#                 if perc > 0 :
#                     deduct_amt = (perc * t_amt)/100
#                     v_list[1] = deduct_amt
#                     v_list[2] = t_amt - deduct_amt
#                     
#                 else :
#                     raise osv.except_osv(_("Warnning"),_("Please Configure the deduction Policy "))
#                 
#             else :
#                 raise osv.except_osv(_("Warnning"),_("Please Configure the deduction Policy"))
#             
#         return v_list
    
    
    def _get_default_partner_val(self):
        if self._context is None:
            self._context = {}
        if 'ids' in self._context:
            coll_obj = self.env['tour.cancellation'].browse(self._context['ids'] )
        return coll_obj.customer_id.id
    
#     def _get_default_partner_val(self, cr, uid, context=None):
#         if context is None:
#             context = {}
#         if 'ids' in context:
#             coll_obj = self.pool.get('tour.cancellation').browse(cr, uid,context['ids'] )
#             
#         return coll_obj.customer_id.id
    
    
#     _defaults = {
#                  'name': lambda *a: 'Tour Cancellation Journal Entry',
#                  'cancellation_id':lambda self,cr,uid,ctx: self._get_default_rec(cr, uid, ctx),
#                  'partner_id': lambda self,cr,uid,ctx: self._get_default_partner_val(cr, uid, ctx),
#                  'refund_amt':lambda self,cr,uid,ctx: self._get_default_val(cr, uid, ctx)[2],
#                  'deduct_amt':lambda self,cr,uid,ctx: self._get_default_val(cr, uid, ctx)[1],
#                  'booking_charge':lambda self,cr,uid,ctx: self._get_default_val(cr, uid, ctx)[0],
#                  }
     
