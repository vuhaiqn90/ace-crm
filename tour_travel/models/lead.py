from odoo import fields, models,api
from odoo.tools.translate import _
from odoo.exceptions import UserError

class crm_lead(models.Model):
    _inherit = 'crm.lead'  
    
    _description ='User Modification'
    
    via = fields.Selection([
                               ('direct','Direct'),
                               ('agent','Agent')
                             ],"Via",default=lambda * a: 'direct')
    agent_id = fields.Many2one('res.partner','Agent')
    lead_sequence = fields.Char('Lead Number', size=64,readonly=True)
              
#     _defaults = {
#                  'via': lambda * a: 'direct',
#                  }
    
#     
    def name_get(self):
        
        res = super(crm_lead, self).name_get()
        if not len(self._ids):
            return []
        res = [(r['id'], r['lead_sequence']) for r in self.read(['lead_sequence'])]
        return res
    
#     def name_get(self, ids, context=None):
#         print("iiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
#         res = []
#         if not len(ids):
#             print("jhggggggggggggggggggggg")
#             return []
#         res = [(r['id'], r['lead_sequence']) for r in self.read(cr, uid, ids, ['lead_sequence'], context)]
#         print("jhjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj",res)
#         return res
    
    
    @api.model
    def create(self,vals): 
        # function overwrites create method and auto generate request no. 
        req_no = self.env['ir.sequence'].get('crm.lead')
        vals['lead_sequence'] = req_no
        return super(crm_lead, self).create(vals)
    
#     def create(self, cr, uid, vals, context=None): 
#         # function overwrites create method and auto generate request no. 
#         req_no = self.pool.get('ir.sequence').get(cr,uid,'crm.lead'),
#         vals['lead_sequence'] = req_no[0]
#         return super(crm_lead, self).create(cr, uid, vals, context=context)
    
    
    @api.multi
    def unlink(self):
        """
        Allows to delete lead which are created once
        """
        for rec in self:
            raise UserError('Cannot delete these Lead.!')
        return super(crm_lead, self).unlink()
    
#     def unlink(self, cr, uid, ids, context):
#         """
#         Allows to delete lead which are created once
#         """
#         for rec in self.browse(cr, uid, ids, context = context):
#             raise osv.except_osv(_('Invalid action !'), _('Cannot delete these Lead.!'))
#         return super(crm_lead, self).unlink(cr, uid, ids, context = context)
    
