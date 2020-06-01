# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class CommissionConfig(models.Model):
    _name = "tmg.membership.level"
    _description = _("TMG Customer Membership Level")
    _order = 'sequence'

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    active = fields.Boolean(default=True)