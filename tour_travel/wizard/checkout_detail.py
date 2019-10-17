from odoo import fields, models, api
from odoo.tools.translate import _

    
class checkout_detail_wizard(models.TransientModel):
    _name = 'checkout_detail.wizard'
    _description ='Customer Checkout Detail Wizard'
    
    
    name = fields.Char('Description',size=100,readonly=True,default=lambda *a: 'Checkout Details Wizard')
    book_id = fields.Many2one('hotel.reservation',"Book ID",readonly=True,default=lambda self: self._get_default_rec())
    order_amt = fields.Float('Order Amount',readonly=True,default=lambda self: self._get_default_val())
    residual_amt = fields.Float('Residual Amount',readonly=True,default=lambda self: self._get_default_actual_residual_amt())
        
    
    def allow_to_send(self):
        room = 0
        for obj in self:
            for line in obj.book_id.room_line_ids:
                print("line",line.required_rooms)
                room = line.room_type_id.available_rooms + line.required_rooms
                line.room_type_id.write({'available_rooms':room})
                line.write({'state':'checked'})
            
            if obj.book_id.room_reserve_invoice_ids[0].state == 'draft':
                raise Warning("Invoice Is Not Validated Yet")
                
            if obj.residual_amt != 0:
                raise Warning("Payment Is Not Received Yet")
            obj.book_id.write({'state':'done'})
        return { 'type':'ir.actions.act_window_close' }
    
    
#     def allow_to_send(self, cr, uid, ids, context=None):
#         room = 0
#         for obj in self.browse(cr,uid,ids):
#             for line in obj.book_id.room_line_ids:
#                 print("line",line.required_rooms)
#                 room = line.room_type_id.available_rooms + line.required_rooms
#     #                 print "roomss",room
#                 self.pool.get('room.info').write(cr, uid, line.room_type_id.id, {'available_rooms':room})
#                 self.pool.get('room.line').write(cr,uid,line.id,{'state':'checked'})
#             
#             if obj.book_id.room_reserve_invoice_ids[0].state == 'draft':
#                 raise osv.except_osv(_("Warnning"),_("Invoice Is Not Validated Yet"))
#                 
#             if obj.residual_amt != 0:
#                 raise osv.except_osv(_("Warnning"),_("Payment Is Not Received Yet"))
#         self.pool.get('hotel.reservation').write(cr, uid, obj.book_id.id, {'state':'done'})
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
            coll_obj = self.env['hotel.reservation'].browse(self._context['ids'] )
            
        return coll_obj.total_amt
    
#     def _get_default_val(self, cr, uid, context=None):
#         if context is None:
#             context = {}
#         if 'ids' in context:
#             coll_obj = self.pool.get('hotel.reservation').browse(cr, uid,context['ids'] )
#             
#         return coll_obj.total_amt
    
    
    def _get_default_actual_residual_amt(self):
        if self._context is None:
            self._context = {}
        if 'ids' in self._context:
            coll_obj = self.env['hotel.reservation'].browse(self._context['ids'] )
            print("coll_obj.deposit_ids",coll_obj.room_reserve_invoice_ids)
            
            for line in coll_obj.room_reserve_invoice_ids:
                if line.state != 'cancel' or line.state != 'paid':
                    ln = line
                    return ln.residual
    
#     def _get_default_actual_residual_amt(self, cr, uid, context=None):
#         if context is None:
#             context = {}
#         if 'ids' in context:
#             coll_obj = self.pool.get('hotel.reservation').browse(cr, uid,context['ids'] )
#             print("coll_obj.deposit_ids",coll_obj.room_reserve_invoice_ids)
#             
#             for line in coll_obj.room_reserve_invoice_ids:
#                 print("line state",line.state)
#                 print("line residual",line.residual)
#                 if line.state != 'cancel' or line.state != 'paid':
#                     ln = line
#                     print("residual",ln.residual)
#         return ln.residual
    
    
    
    
#     _defaults = {
#         'name': lambda *a: 'Checkout Details Wizard', 
#         'book_id':lambda self,cr,uid,ctx: self._get_default_rec(cr, uid, ctx),
#         'order_amt':lambda self,cr,uid,ctx: self._get_default_val(cr, uid, ctx),
#         'residual_amt':lambda self,cr,uid,ctx: self._get_default_actual_residual_amt(cr, uid, ctx),
#     }
