# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools.misc import formatLang
import odoo.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('product_id')
    def get_analytic_tags(self):
        if self.product_id and self.product_id.analytic_tag_ids:
            self.analytic_tag_ids = [(4, tag.id) for tag in self.product_id.analytic_tag_ids]