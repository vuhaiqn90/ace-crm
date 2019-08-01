# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SMSMarketingGroup(models.Model):
    _name = 'sms.marketing.group'

    name = fields.Char()
    partner_ids = fields.Many2many('res.partner', 'sms_marketing_group_partner_rel', 'group_id', 'partner_id',
                                   string="Partners")
