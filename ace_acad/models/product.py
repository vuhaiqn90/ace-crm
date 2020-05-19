# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    request_cost = fields.Boolean('Request for Cost')
    request_url = fields.Char('URL')