# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    telesales = fields.Many2one('res.users')