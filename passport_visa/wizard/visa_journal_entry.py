from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, Warning


    
class visa_journal_entry_wizard(models.TransientModel):
    _name = 'visa_journal_entry.wizard'
    
    _description ='Visa_journal_entry Detail Wizard'
    
    
    name = fields.Char('Description',size=100,readonly=True,default=lambda *a: 'Visa Account Journal Entry')
    visa_id = fields.Many2one('visa.booking',"Visa Booking ID",readonly=True, default = lambda self: self._get_default_rec())
    partner_id = fields.Many2one('res.partner',"Customer",readonly=True,default=lambda self: self._get_default_partner_val())
    payment_date = fields.Date('Payment Date',required=True)
    journal_id = fields.Many2one('account.journal',"Journal",required=True)
    #                  'period_id': fields.many2one('account.period',"Period",required=True),
    service_cost = fields.Float('Service Cost',compute="visa_cal")
        
    #

    @api.depends('visa_id.scheme_id.cost_price')
    def visa_cal(self):
        self.service_cost=self.visa_id.scheme_id.cost_price
    def allow_to_send(self):
        
        for obj in self:
            
            if obj.visa_id.visa_invoice_ids[0].state != 'paid':
                raise Warning("Invoice Is Not Paid Yet. Please Pay The Invoice Amount")
            move_id = self.env['account.move'].create(
                                {
                                   'journal_id': obj.journal_id.id,
                                   'name': obj.name ,
#                                    'period_id':obj.period_id.id,#does not exist
                                   'ref': obj.visa_id.name,
                               })
            move_line1 = {
                         
                       'name': obj.name,
                       'move_id': move_id.id,
                       'account_id': obj.journal_id.default_credit_account_id.id,
                       'debit': obj.service_cost,
                       'credit': 0.0,
#                        'period_id':obj.period_id.id, #does not exist
                       'ref': obj.visa_id.name,
                       'journal_id': obj.journal_id.id,
                       'partner_id': obj.partner_id.id,
                       'date': obj.payment_date
                       }
           
            move_line2 = {
                          'name': obj.name,
                          'move_id': move_id.id,
                          'account_id': obj.journal_id.default_credit_account_id.id,
                          'debit':0.0,
                          'credit':  obj.service_cost,
#                           'period_id':obj.period_id.id,#does not exist
                          'ref': obj.visa_id.name,
                          'journal_id': obj.journal_id.id,
                          'partner_id': obj.partner_id.id,
                          'date': obj.payment_date
                           }
           
            move_id.write({'line_ids':[(0,0,move_line1),(0,0,move_line2)]})
            
            obj.visa_id.write({'state':'in_process'})
        return { 'type':'ir.actions.act_window_close' }
    
    
    @api.model
    def _get_default_rec(self):
        if self._context.get('ids'):
            return self._context.get('ids')

    @api.model
    def _get_default_val(self):
        if self._context.get('ids'):
            coll_id = self.env['visa.booking'].search([('id', 'in', [self._context.get('ids')])], limit=1)
        return coll_id.product_id.standard_price

    @api.model
    def _get_default_partner_val(self):
        if self._context.get('ids'):
            coll_id = self.env['visa.booking'].search([('id', 'in', [self._context.get('ids')])], limit=1)
        return coll_id.customer_id.id
    
    
#     _defaults = {
#         'name': lambda *a: 'Visa Account Journal Entry', 
#         'visa_id':lambda self,cr,uid,ctx: self._get_default_rec(cr, uid, ctx),
#         'partner_id': lambda self,cr,uid,ctx: self._get_default_partner_val(cr, uid, ctx),
#         'service_cost':lambda self,cr,uid,ctx: self._get_default_val(cr, uid, ctx),
#                   }

