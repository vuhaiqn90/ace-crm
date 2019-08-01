# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def create(self, vals):
        product = super(ProductTemplate, self).create(vals)
        if product.recurring_invoice and not product.subscription_template_id:
            template_id = self.env['sale.subscription.template'].create({
                'name': product.display_name,
                'recurring_interval': 1,
                'recurring_rule_type': 'yearly',
                'recurring_rule_boundary': 'limited',
            })
            product.subscription_template_id = template_id.id
        return product