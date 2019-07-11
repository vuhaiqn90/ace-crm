# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ACERateDiscount(models.Model):
    _name = 'ace.rate.discount'

    sequence = fields.Integer('Sequence #')
    name = fields.Char()
    rate = fields.Float()
    # type = fields.Selection([('amount', 'Amount'), ('percent', 'Percentage')], default='percent')
    user_ids = fields.Many2many('res.users', 'rate_discount_users_rel', 'rate_id', 'user_id', 'Users')