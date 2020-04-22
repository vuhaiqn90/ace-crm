# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('product_id')
    def get_analytic_tags(self):
        if self.product_id and self.product_id.analytic_tag_ids:
            self.analytic_tag_ids = [(4, tag.id) for tag in self.product_id.analytic_tag_ids]

    @api.model
    def create(self, vals):
        line_id = super(SaleOrderLine, self).create(vals)
        if line_id.product_id and line_id.product_id.analytic_tag_ids:
            line_id.write({'analytic_tag_ids': [(4, tag.id) for tag in line_id.product_id.analytic_tag_ids]})
        return line_id