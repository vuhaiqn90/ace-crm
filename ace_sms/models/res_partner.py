# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResPartnerSms(models.Model):
    _inherit = "res.partner"

    sms_message_count = fields.Integer(compute='_compute_sms_message_count')

    @api.multi
    def _compute_sms_message_count(self):
        for partner in self:
            partner.sms_message_count = self.env['sms.message'].search_count([('partner_id', '=', partner.id)])

    @api.multi
    def open_sms_messages(self):
        partner_ids = self.ids
        action = self.env.ref('ace_sms.sms_message_action').read()[0]
        action['domain'] = [('partner_id', 'in', partner_ids)]
        return action
#
#     @api.one
#     @api.onchange('country_id','mobile')
#     def _onchange_mobile(self):
#         """Tries to convert a local number to e.164 format based on the partners country, don't change if already in e164 format"""
#         if self.mobile:
#
#             if self.country_id and self.country_id.mobile_prefix:
#                 if self.mobile.startswith("0"):
#                     self.mobile = self.country_id.mobile_prefix + self.mobile[1:].replace(" ","")
#                 elif self.mobile.startswith("+"):
#                     self.mobile = self.mobile.replace(" ","")
#                 else:
#                     self.mobile = self.country_id.mobile_prefix + self.mobile.replace(" ","")
#             else:
#                 self.mobile = self.mobile.replace(" ","")