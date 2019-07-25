# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.addons.ace_sms.models.esms_request import ESMSProvider

class SmsBrand(models.Model):
    _name = 'sms.brand'
    _description = 'SMS Brand'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Brand Code', required=True)
    gateway_id = fields.Many2one('sms.gateway', string="Account Gateway", required=True)

    @api.model
    def send_message(self, to_number, sms_content, my_model_name='', my_record_id=0):
        """Send a message from this account"""
        esms = ESMSProvider(self.gateway_id.base_url, self.gateway_id.api_key, self.gateway_id.secret_key)
        resp = esms.send_sms({
            'Phone': to_number,
            'Content': sms_content,
            'Phone': to_number,
            'IsUnicode': 0,
            'Brandname': self.name,
            'SmsType': self.code,
            'Sandbox': 0,
        })
        return resp


    @api.model
    def check_all_messages(self):
        """Check for any messages that might have been missed during server downtime"""
        my_accounts = self.env['sms.account'].search([])
        for sms_account in my_accounts:
            self.env[sms_account.account_gateway_id.gateway_model_name].check_messages(sms_account.id)