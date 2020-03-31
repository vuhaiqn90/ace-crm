# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class MembershipLevel(models.Model):
    _name = 'membership.level'

    sequence = fields.Integer()
    name = fields.Char()
    code = fields.Char()
    point = fields.Float()
    referring_percent = fields.Float('Referring Percent', help='Percentage of points earned for referrals')