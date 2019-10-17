from odoo import fields, models

class sale_order(models.Model):
    _inherit = 'sale.order'
    
    order_policy = fields.Selection([
            ('prepaid', 'Payment Before Delivery'),
            ('manual', 'Shipping & Manual Invoice'),
            ('postpaid', 'Invoice on Order After Delivery'),
            ('picking', 'Invoice from the Packing'),
        ], string='Shipping Policy',default='prepaid')
    
#     _defaults = {
#                     'order_policy':'prepaid',
#                 }
