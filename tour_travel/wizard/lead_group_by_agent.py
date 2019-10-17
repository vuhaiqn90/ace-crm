from odoo import fields, models, api
from odoo.tools.translate import _


    
class leads_group_by_agent_wizard(models.TransientModel):
    _name = 'leads.group.by.agent.wizard'
    _description ='leads by Agent '
    
    
    name = fields.Char('Description',size=100,readonly=True)
    partner_ids = fields.Many2many("res.partner","crm_partner_rel",'agent_lead_id','partner_id','Agent')
    report_basis = fields.Selection([
                                   ('direct','Direct'),
                                   ('agent','Agent')
                                 ],"Report Basis",required=True,default='direct')
    categ_ids = fields.Many2many('res.partner.category','crm_case_agent_rel','crm_case_id','categ_id','Category')
    start_date = fields.Date("Start Date",required=True)
    end_date = fields.Date("End Date",required=True)
    
    
#     _defaults = {
#         'report_basis': 'direct',
#     }
    
    
    def print_report(self):
        data = {}
        if self._context is None:
            self._context = {}
        data['form'] = self.read(['start_date','end_date','categ_ids','report_basis','partner_ids'])[0]
        data['ids'] = self._context.get('active_ids', [])
        data['model'] = self._context.get('active_model', 'ir.ui.menu')
        if data['form']['start_date'] > data['form']['end_date']:
            raise Warning('Please Check the start and end date !!')
        if data['form']['report_basis'] =='agent':
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'lead.report.group.by.agent',
                    'datas': data,
                    }
        else:
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'lead.report.by.direct',
                    'datas': data,
                    }
    
#     def print_report(self, cr, uid, ids, context=None):
#         data = {}
#         if context is None:
#             context = {}
#         data['form'] = self.read(cr, uid, ids, ['start_date','end_date','categ_ids','report_basis','partner_ids'])[0]
#         data['ids'] = context.get('active_ids', [])
#         data['model'] = context.get('active_model', 'ir.ui.menu')
#         if data['form']['start_date'] > data['form']['end_date']:
#             raise osv.except_osv(('warning'),('Please Check the start and end date !!'))
#         if data['form']['report_basis'] =='agent':
#             return {
#                     'type': 'ir.actions.report.xml',
#                     'report_name': 'lead.report.group.by.agent',
#                     'datas': data,
#                     }
#         else:
#             return {
#                     'type': 'ir.actions.report.xml',
#                     'report_name': 'lead.report.by.direct',
#                     'datas': data,
#                     }
             
