# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags',
                                        related='sale_line_id.analytic_tag_ids')