from odoo import fields, models, api
from odoo.tools.translate import _

    
class leads_by_agent_wizard(models.TransientModel):
    _name = 'leads.by.agent.wizard'
    _description ='leads by Agent '
    
    
    name = fields.Char('Description',size=100,readonly=True)
    partner_id = fields.Many2one("res.partner","Agent")
    report_basis = fields.Selection([
                                   ('direct','Direct'),
                                   ('agent','Agent')
                                 ],"Report Basis",required=True,default='direct')
    categ_id = fields.Many2one('res.partner.category','Category')  
    start_date = fields.Date("Start Date",required=True)
    end_date = fields.Date("End Date",required=True)
    
    
#     _defaults = {
#         'report_basis': 'direct',
#     }
    
    
    def print_report(self):
        data = {}
        if self._context is None:
            self._context = {}
        data['form'] = self.read(['start_date','end_date','categ_id','report_basis','partner_id'])[0]
        data['ids'] = self._context.get('active_ids', [])
        data['model'] = self._context.get('active_model', 'ir.ui.menu')
        if data['form']['start_date'] > data['form']['end_date']:
            raise ('Please Check the start and end date !!')
        
        return {
           'type': 'ir.actions.report.xml',
           'report_name': 'lead.report.by.agent',
           'datas': data,
        }
    
#     def print_report(self, cr, uid, ids, context=None):
#         data = {}
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
#         } 
             
