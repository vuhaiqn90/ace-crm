# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    request_quote = fields.Boolean('Request for quote')
    request_url = fields.Char('Quote URL')