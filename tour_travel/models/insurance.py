from odoo import fields, models, api
from odoo.tools.translate import _


class insurance_type(models.Model):
    _name = "insurance.type"
    _description = "Documents Management For Tours and Travel Services"

    name = fields.Char("Name", size=50, required=True)
    code = fields.Char('Code', size=164, required=True)
    adult_cost = fields.Float('For Adults Insurance Cost', size=164, required=True)
    child_cost = fields.Float('For Child Insurance Cost', size=164, required=True)


class insurance_policy(models.Model):
    _name = "insurance.policy"
    _description = "Insurance Policy "

    insurance_type_id = fields.Many2one('insurance.type', 'Insurance', required=True)
    name = fields.Char("Insurance Name", size=50, required=True)
    insurance_cost_for_adults = fields.Float('Insurance Cost For Adults', size=164, required=True)
    insurance_cost_for_childs = fields.Float('Insurance Cost For Child', size=164, required=True)
    coverage_line_ids = fields.One2many('insurance.coverage.line', 'insurance_policy_id', 'Insurance Coverage Line')
    state = fields.Selection([
                               ('draft', 'Draft'),
                               ('confirm', 'Confirm'),
                               ], 'Status', readonly=False, default=lambda *a: 'draft')
    
    @api.onchange('insurance_type_id')
    def on_change_type_id(self):
        result = {}
        result['name'] = self.insurance_type_id.name
        result['insurance_cost_for_adults'] = self.insurance_type_id.adult_cost
        result['insurance_cost_for_childs'] = self.insurance_type_id.child_cost
        return {'value': result}
    
#     def on_change_type_id(self,cr,uid,ids,insurance_type_id):
#         result = {}
#         obj = self.pool.get('insurance.type').browse(cr,uid,insurance_type_id)
#         result['name']= obj.name
#         result['insurance_cost_for_adults']= obj.adult_cost
#         result['insurance_cost_for_childs']= obj.child_cost
#         return {'value':result}

    def button_confirm(self):
        return self.write({'state': 'confirm'})
    
#     def button_confirm(self, cr, uid, ids, context=None):
#         return self.write(cr, uid, ids, {'state':'confirm'})
   
#     _defaults = {
#                  'state': lambda *a: 'draft',
#                  }
    

class insurance_coverage_line(models.Model):
    _name = "insurance.coverage.line"
    _description = "insurance coverage for Tours and Travel Services"

    product_id = fields.Many2one("product.product", 'Coverage', required=True)
    name = fields.Char("Coverage Name", size=50, required=True)
    benifit_cost = fields.Float('Benifit Cost', size=164, required=True)
    insurance_policy_id = fields.Many2one("insurance.policy", 'Insurance Policy ID', required=True)
    
    @api.onchange('product_id')
    def on_change_product_id(self):
        result = {}
        result['name'] = self.product_id.name
        return {'value': result}
    
#     def on_change_product_id(self,cr,uid,ids,product_id):
#         result = {}
#         obj = self.pool.get('product.product').browse(cr,uid,product_id)
#         result['name']= obj.name
#         return {'value':result}
