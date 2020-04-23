# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class CommissionConfig(models.Model):
    _name = "ace.commission.config"
    _description = _("Commission Config")
    _order = 'sequence'

    sequence = fields.Integer(default=10)
    name = fields.Char()
    type = fields.Selection([('sale', 'Salesperson'), ('tels', 'Telesales'), ('ctv', 'CTV')])
    trial = fields.Boolean(string='Trial Work')
    total = fields.Float()
    rate = fields.Float(string='Rate(%)')
    delta_method = fields.Boolean(string='Delta Method',
                                  help="If Delta Method is True, amount to compute commission = (total revenue of staff - Total) * rate / 100."
                                       "Otherwise, amount to compute commission = total revenue of staff * rate / 100")

