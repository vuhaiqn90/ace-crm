# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.osv import osv

from odoo.addons.ace_sms.models.esms_request import ESMSProvider
from werkzeug import urls


class SmsGateway(models.Model):
    _name = 'sms.gateway'
    _description = 'SMS Gateway'
    
    name = fields.Char(required=True, string='Gateway Name')
    base_url = fields.Char(required=True, string='Base URL')
    api_key = fields.Char(required=True, string='API Key')
    secret_key = fields.Char(required=True, string='Secret Key')
    brand_ids = fields.One2many('sms.brand', 'gateway_id', string='SMS Brands')

    @api.multi
    def connect_sms(self):
        for r in self:
            esms = ESMSProvider(self.base_url, self.api_key, self.secret_key)
            resp = esms.account_info()
            if resp.get('CodeResponse', '-9999') == '100':
                raise osv.except_osv("Connection Test Succeeded!",
                                     u"Thông tin tài khoản \n 1. UserID: %s \n 2. Số dư: %s" % (resp.get('UserID'), resp.get('Balance')))
            else:
                raise osv.except_osv("Connection Test Failed!",
                                     u" %s" % resp.get('Exception'))
        return True
