from odoo import fields, models, api
from odoo.tools.translate import _


    
class transport_checkout_detail_wizard(models.TransientModel):
    _name = 'transport_checkout_detail.wizard'
    _description ='Transport Checkout Detail Wizard'
    
    
    name = fields.Char('Description',size=100,readonly=True,default=lambda *a: 'Checkout Details Wizard')
    transport_book_id = fields.Many2one('transport.book',"Transport Book ID",readonly=True,default=lambda self: self._get_default_rec())
    order_amt = fields.Float('Order Amount',readonly=True,default=lambda self: self._get_default_val())
    residual_amt = fields.Float('Residual Amount',readonly=True,default=lambda self: self._get_default_actual_residual_amt())

    
    @api.multi
    def allow_to_send(self):
        transport = 0
        for obj in self:
            for line in obj.transport_book_id.transport_line_ids:
                transport = line.available_vehicle + line.required_vehicle
                line.transport_type_info_id.write({'available_vehicle':transport})
            if obj.transport_reserve_invoice_ids[0].state == 'draft':
                raise Warning("Invoice Is Not Validated Yet")
                
            if obj.residual_amt != 0:
                raise Warning("Payment Is Not Received Yet")
            obj.transport_book_id.write({'state':'done'})
        return { 'type':'ir.actions.act_window_close' }
    
#     def allow_to_send(self, cr, uid, ids, context=None):
#         transport = 0
#         for obj in self.browse(cr,uid,ids):
#         
#             for line in obj.transport_book_id.transport_line_ids:
#         
#                 transport = line.available_vehicle + line.required_vehicle
#                 
#                 self.pool.get('transport.type.info').write(cr, uid, line.transport_type_info_id.id, {'available_vehicle':transport})
#         
#             if obj.transport_reserve_invoice_ids[0].state == 'draft':
#                 raise osv.except_osv(_("Warnning"),_("Invoice Is Not Validated Yet"))
#                 
#             if obj.residual_amt != 0:
#                 raise osv.except_osv(_("Warnning"),_("Payment Is Not Received Yet"))
#         self.pool.get('transport.book').write(cr, uid, obj.transport_book_id.id, {'state':'done'})
#         return { 'type':'ir.actions.act_window_close' }
    
    
    def _get_default_rec(self):
        if self._context is None:
            self._context = {}
        if 'ids' in self._context:
            res=self._context['ids']
        return res
    
#     def _get_default_rec(self, cr, uid, context=None):
#         print("context",context)
#         if context is None:
#             context = {}
#         if 'ids' in context:
#             res=context['ids']
#         return res    
    
     
    def _get_default_val(self):
        if self._context is None:
            self._context = {}
        if 'ids' in self._context:
            coll_obj = self.env['transport.book'].browse(self._context['ids'] )
            return coll_obj.total_amt
     
#     def _get_default_val(self, cr, uid, context=None):
#         if context is None:
#             context = {}
#         if 'ids' in context:
#             coll_obj = self.pool.get('transport.book').browse(cr, uid,context['ids'] )
#             
#         return coll_obj.total_amt
     
    
    def _get_default_actual_residual_amt(self):
        if self._context is None:
            self._context = {}
        if 'ids' in self._context:
            coll_obj = self.env['transport.book'].browse(self._context['ids'] )
            for line in coll_obj.transport_reserve_invoice_ids:
                if line.state != 'cancel' or line.state != 'paid':
                    ln = line
                return ln.residual
      
#     def _get_default_actual_residual_amt(self, cr, uid, context=None):
#         if context is None:
#             context = {}
#         if 'ids' in context:
#             coll_obj = self.pool.get('transport.book').browse(cr, uid,context['ids'] )
#         #            print "coll_obj.deposit_ids",coll_obj.room_reserve_invoice_ids
#             
#             for line in coll_obj.transport_reserve_invoice_ids:
#         #                print "line state",line.state
#         #                print "line residual",line.residual
#                 if line.state != 'cancel' or line.state != 'paid':
#                     ln = line
#         #                    print "residual",ln.residual
#                 return ln.residual
    
    
#     _defaults = {
#         'name': lambda *a: 'Checkout Details Wizard', 
#         'transport_book_id':lambda self,cr,uid,ctx: self._get_default_rec(cr, uid, ctx),
#         'order_amt':lambda self,cr,uid,ctx: self._get_default_val(cr, uid, ctx),
#         'residual_amt':lambda self,cr,uid,ctx: self._get_default_actual_residual_amt(cr, uid, ctx),
#     }
