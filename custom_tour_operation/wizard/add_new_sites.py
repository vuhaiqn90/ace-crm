from odoo import fields, models, api
from odoo.tools.translate import _


    
class add_sites_wizard1(models.TransientModel):
    _name = 'add.sites.wizard1'
    _description ='Customer Checkout Detail Wizard'
    
    
    tour_day = fields.Many2one('tour.days',string='Days',required=True,readonly=True,default=_get_default_value1)
    sites_details = fields.Many2many('product.product','site_wizard_relation','pragram_ids','wizard_ids',string='Sites Name',domain=[('type','=','service'),('categ_id','=',8)])
        
    
    @api.multi
    def add_sites_form(self):
        tour_program_browse = self.env['custom.tour.programme'].browse(self._context['active_id'])
        dec = tour_program_browse.description or ''
        for obj in self:
            for line in obj.sites_details:
                dec += line.name + ', '
                self._cr.execute("""select id from tour_sites where name=%s and program_id1=%s""",(line.id,obj.tour_day.id))                      
                p_id = self._cr.fetchone()
                if p_id:
                    raise Warning("Site '%s' is all ready added to the list."% (line.name))
                self.env['tour.sites'].create({'program_id1':obj.tour_day.id,'name': line.id})
            
            tour_program_browse.write({'description':dec})
        return { 'type':'ir.actions.act_window_close' }
    
#     def add_sites_form(self, cr, uid, ids, context=None):
#         print "add_sites",context,"context"
#         tour_program_browse = self.pool.get('custom.tour.programme').browse(cr,uid,context['active_id'])
#         dec = tour_program_browse.description or ''
#         for obj in self.browse(cr,uid,ids):
#             print obj,"obj",obj.sites_details
#             for line in obj.sites_details:
#                 print "line",line.id,obj.tour_day.id
#                 dec += line.name + ', '
#                 cr.execute("""select id from tour_sites where name=%s and program_id1=%s""",(line.id,obj.tour_day.id))                      
#                 p_id = cr.fetchone()
#                 if p_id:
#                     raise osv.except_osv(_('Warning!'), _("Site '%s' is all ready added to the list.") % (line.name))
#                 self.pool.get('tour.sites').create(cr, uid, {'program_id1':obj.tour_day.id,'name': line.id})
#             
#             self.pool.get('custom.tour.programme').write(cr, uid, context['active_id'], {'description':dec})
#         return { 'type':'ir.actions.act_window_close' }
    
    
    def _get_default_value1(self):
        if self._context is None:
            self._context = {}
        if 'ids' in self._context:
            coll_obj = self.env['tour.days'].browse(self._context['ids'] )
        return coll_obj.id
    
#     def _get_default_value1(self, cr, uid, context=None):
#         if context is None:
#             context = {}
#         print context,"context"
#         if 'ids' in context:
#             coll_obj = self.pool.get('tour.days').browse(cr, uid,context['ids'] )
#             print coll_obj,"coll_obj"
#         return coll_obj.id
    
#     _defaults = {
#         'tour_day': lambda self,cr,uid,ctx: self._get_default_value1(cr, uid, ctx),
#                   }
     
