from odoo import fields,models,api
from odoo.tools.translate import _


class passport_booking(models.Model):
    _inherit = "passport.booking"
    _description = " Passport booking class "
    
    
    tour_book_id = fields.Many2one('tour.booking', 'Tour Booking Ref', readonly=True)
    tour_id = fields.Many2one('tour.package', 'Tour', readonly=True)
    tour_date = fields.Date('Tour Date', readonly=True)
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)]})
    
    
    @api.multi
    def approve_document(self):
        for obj in self:
            if not obj.attachment_line_ids:
                raise Warning("Documents not verified. Please verify documents and make attachment")
            if obj.tour_book_id:
                self.write({'state' : 'invoice'})
            else:
                self.write({'state' : 'approve'})
        return True
    
#     def approve_document(self, cr, uid, ids, context=None):
#         for obj in self.browse(cr,uid,ids):
#             if not obj.attachment_line_ids:
#                 raise osv.except_osv(_("Warnning"),_("Documents not verified. Please verify documents and make attachment"))
#             if obj.tour_book_id:
#                 self.write(cr, uid, ids, {'state':'invoice'})
#             else:
#                 self.write(cr, uid, ids, {'state':'approve'})
#         return True
    
    
    
class visa_booking(models.Model):
    _inherit = "visa.booking"
    
    _description = "Visa Booking Inherit"
    
    tour_book_id = fields.Many2one('tour.booking', 'Tour Booking Ref', readonly=True)
    tour_id = fields.Many2one('tour.package', 'Tour', readonly=True)
    tour_date = fields.Date('Tour Date', readonly=True)
    
    
    @api.multi
    def approve_document(self):
        for obj in self:
            if not obj.attachment_line_ids:
                raise Warning("Documents not verified. Please verify documents and make attachment")
            if obj.tour_book_id:
                self.write({'state' : 'invoice'})
            else:
                self.write({'state' : 'approve'})
        return True
    
#     def approve_document(self, cr, uid, ids, context=None):
#         for obj in self.browse(cr,uid,ids):
#             if not obj.attachment_line_ids:
#                 raise osv.except_osv(_("Warnning"),_("Documents not verified. Please verify documents and make attachment"))
#             if obj.tour_book_id:
#                 self.write(cr, uid, ids, {'state':'invoice'})
#             else:
#                 self.write(cr, uid, ids, {'state':'approve'})
#         return True
    

class passport_journal_entry_wizard(models.TransientModel):
    
    _inherit = 'passport_journal_entry.wizard'
    _description ='passport_journal_entry Detail Wizard'
    
    
    @api.multi
    def allow_to_send(self):
        for obj in self:
            if not obj.passport_id.tour_book_id:
                if obj.passport_id.passport_invoice_ids[0].state != 'paid':
                    raise Warning("Invoice Is Not Paid Yet. Please Pay The Invoice Amount")
            
            move_id = self.env['account.move'].create({
                                   'journal_id': obj.journal_id.id,
                                   'ref': obj.passport_id.name,
                               })
            acc_id = obj.passport_id.product_id.property_account_expense_id.id
            if not acc_id:
                acc_id = obj.passport_id.product_id.categ_id.property_account_expense_categ_id.id
            if not acc_id:
                raise Warning("No Expense Account Defined for Service Product. Please Select Expense Account Product ")+_(obj.passport_id.product_id.name)
                
            move_line1 = {
                       'name': obj.name,
                       'move_id': move_id.id,
                       'account_id': acc_id,
                       'debit': obj.service_cost,
                       'credit': 0.0,
                       'ref': obj.passport_id.name,
                       'journal_id': obj.journal_id.id,
                       'partner_id': obj.partner_id.id,
                       'date' : obj.payment_date
                       }
           
            move_line2 = {
                          'name': obj.name,
                          'move_id': move_id.id,
                          'account_id': obj.journal_id.default_credit_account_id.id,
                          'debit': 0.0,
                          'credit': obj.service_cost,
                          'ref': obj.passport_id.name,
                          'journal_id': obj.journal_id.id,
                          'partner_id': obj.partner_id.id,
                          'date': obj.payment_date
                           }
            
            move_id.write({'line_ids': [(0,0,move_line1),(0,0,move_line2)], 'state': 'posted'})
            
            obj.passport_id.write({'state':'in_process'})
        return { 'type': 'ir.actions.act_window_close' }
    
#     def allow_to_send(self, cr, uid, ids, context=None):
#         for obj in self.browse(cr,uid,ids):
#             if not obj.passport_id.tour_book_id:
#                 if obj.passport_id.passport_invoice_ids[0].state != 'paid':
#                     raise osv.except_osv(_("Warnning"),_("Invoice Is Not Paid Yet. Please Pay The Invoice Amount"))
#             
#             move_id = self.pool.get('account.move').create(cr, uid,
#                                 {
#                                    'journal_id': obj.journal_id.id,
#     #                                     'period_id':obj.period_id.id,
#                                    'ref': obj.passport_id.name,
#                                })
#             acc_id = obj.passport_id.product_id.property_account_expense_id.id
#             if not acc_id:
#                 acc_id = obj.passport_id.product_id.categ_id.property_account_expense_categ_id.id
#             if not acc_id:
#                 raise osv.except_osv(_("Warnning"),_("No Expense Account Defined for Service Product. Please Select Expense Account Product ")+_(obj.passport_id.product_id.name))
#                 
#             move_line1 = {
#                          
#                        'name': obj.name,
#                        'move_id': move_id,
#                        'account_id': acc_id,
#                        'debit': obj.service_cost,
#                        'credit': 0.0,
#     #                         'period_id':obj.period_id.id,
#                        'ref': obj.passport_id.name,
#                        'journal_id': obj.journal_id.id,
#                        'partner_id': obj.partner_id.id,
#                        'date': obj.payment_date
#                        }
#            
#             move_line2 = {
#                           'name': obj.name,
#                           'move_id': move_id,
#                           'account_id': obj.journal_id.default_credit_account_id.id,
#                           'debit':0.0,
#                           'credit':  obj.service_cost,
#     #                            'period_id':obj.period_id.id,
#                           'ref': obj.passport_id.name,
#                           'journal_id': obj.journal_id.id,
#                           'partner_id': obj.partner_id.id,
#                           'date': obj.payment_date
#                            }
#             
#             self.pool.get('account.move').write(cr, uid, [move_id], {'line_ids':[(0,0,move_line1),(0,0,move_line2)], 'state':'posted'})
#             
#             self.pool.get('passport.booking').write(cr, uid, obj.passport_id.id, {'state':'in_process'})
#         return { 'type':'ir.actions.act_window_close' }
    
    
          
class visa_journal_entry_wizard(models.TransientModel):
    _inherit = 'visa_journal_entry.wizard'
    _description ='Visa_journal_entry Detail Wizard'
    
    
    @api.multi
    def allow_to_send(self):
        for obj in self:
            if not obj.visa_id.tour_book_id:
                if obj.visa_id.visa_invoice_ids[0].state != 'paid':
                    raise Warning("Invoice Is Not Paid Yet. Please Pay The Invoice Amount")
            acc_id = obj.visa_id.product_id.property_account_expense_id.id
            if not acc_id:
                acc_id = obj.visa_id.product_id.categ_id.property_account_expense_categ_id.id
            if not acc_id:
                raise Warning("No Expense Account Defined for Service Product. Please Select Expense Account Product ")+_(obj.passport_id.product_id.name)
            name = ''
            if obj.journal_id.sequence_id:
                name = self.env['ir.sequence'].get_id(obj.journal_id.sequence_id.id)
            
            move_id = self.env['account.move'].create({
                                   'journal_id': obj.journal_id.id,
                                   'name': name or  obj.name,
                                   'ref': obj.visa_id.name,
                               })
                
            move_line1 = {
                       'name':name or obj.name,
                       'move_id': move_id.id,
                       'account_id': acc_id,
                       'debit': obj.service_cost,
                       'credit': 0.0,
                       'ref': obj.visa_id.name,
                       'journal_id': obj.journal_id.id,
                       'partner_id': obj.partner_id.id,
                       'date': obj.payment_date
                       }
           
            move_line2 = {
                          'name': name or obj.name,
                          'move_id': move_id.id,
                          'account_id': obj.journal_id.default_credit_account_id.id,
                          'debit':0.0,
                          'credit':  obj.service_cost,
                          'ref': obj.visa_id.name,
                          'journal_id': obj.journal_id.id,
                          'partner_id': obj.partner_id.id,
                          'date': obj.payment_date
                           }
            
            move_id.write({'line_ids': [(0, 0, move_line1),(0, 0, move_line2)], 'state': 'posted'})
            
            obj.visa_id.write({'state': 'in_process'})
        return { 'type': 'ir.actions.act_window_close' }
    
#     def allow_to_send(self, cr, uid, ids, context=None):
#         
#         for obj in self.browse(cr,uid,ids):
#             if not obj.visa_id.tour_book_id:
#                 if obj.visa_id.visa_invoice_ids[0].state != 'paid':
#                     raise osv.except_osv(_("Warning"),_("Invoice Is Not Paid Yet. Please Pay The Invoice Amount"))
#             acc_id = obj.visa_id.product_id.property_account_expense_id.id
#             if not acc_id:
#                 acc_id = obj.visa_id.product_id.categ_id.property_account_expense_categ_id.id
#             if not acc_id:
#                 raise osv.except_osv(_("Warnning"),_("No Expense Account Defined for Service Product. Please Select Expense Account Product ")+_(obj.passport_id.product_id.name))
#             name = ''
#             seq_obj = self.pool.get('ir.sequence')
#             if obj.journal_id.sequence_id:
#                 name = seq_obj.get_id(cr, uid, obj.journal_id.sequence_id.id)
#             
#             move_id = self.pool.get('account.move').create(cr, uid,
#                                 {
#                                    'journal_id': obj.journal_id.id,
#                                    'name': name or  obj.name,
#     #                                     'period_id':obj.period_id.id,
#                                    'ref': obj.visa_id.name,
#                                })
#                 
#             move_line1 = {
#                          
#                        'name':name or obj.name,
#                        'move_id': move_id,
#                        'account_id': acc_id,
#                        'debit': obj.service_cost,
#                        'credit': 0.0,
#     #                         'period_id':obj.period_id.id,
#                        'ref': obj.visa_id.name,
#                        'journal_id': obj.journal_id.id,
#                        'partner_id': obj.partner_id.id,
#                        'date': obj.payment_date
#                        }
#            
#             move_line2 = {
#                           'name': name or obj.name,
#                           'move_id': move_id,
#                           'account_id': obj.journal_id.default_credit_account_id.id,
#                           'debit':0.0,
#                           'credit':  obj.service_cost,
#     #                            'period_id':obj.period_id.id,
#                           'ref': obj.visa_id.name,
#                           'journal_id': obj.journal_id.id,
#                           'partner_id': obj.partner_id.id,
#                           'date': obj.payment_date
#                            }
#             
#             self.pool.get('account.move').write(cr, uid, [move_id], {'line_ids':[(0,0,move_line1),(0,0,move_line2)],'state':'posted'})
#             
#             self.pool.get('visa.booking').write(cr, uid, obj.visa_id.id, {'state':'in_process'})
#         return { 'type':'ir.actions.act_window_close' }
     

