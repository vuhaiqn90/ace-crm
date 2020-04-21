# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools.misc import formatLang
import odoo.addons.decimal_precision as dp


class ProductCategory(models.Model):
    _inherit = "product.category"

    analytic_tag_ids = fields.Many2many('account.analytic.tag', 'product_category_analytic_tag_rel',
                                        'category_id', 'analytic_tag_id', string='Analytic Tags')