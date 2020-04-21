# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools.misc import formatLang
import odoo.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"

    analytic_tag_ids = fields.Many2many('account.analytic.tag', 'product_analytic_tag_rel',
                                        'product_id', 'analytic_tag_id', string='Analytic Tags')

    @api.onchange('categ_id')
    def get_analytic_tags(self):
        self.analytic_tag_ids = False
        if self.categ_id and self.categ_id.analytic_tag_ids:
            self.analytic_tag_ids = [(6, 0, self.categ_id.analytic_tag_ids.ids)]
