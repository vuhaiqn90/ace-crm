# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)

from odoo import api, fields, models

class SmsMessageStatus(models.Model):
    _name = "sms.message.status"
    _description = "SMS Message Status"
    
    name = fields.Char(string="Name", readonly=True)
    code = fields.Char(string="Code", readonly=True)
    gateway_id = fields.Many2one('sms.gateway', string="Account Gateway", required=True)

    @api.model
    def get_status(self, gateway_id):
        res = {}
        for s in self.search([('gateway_id', '=', gateway_id)]):
            if s.code not in res:
                res[s.code] = s.id
        return res