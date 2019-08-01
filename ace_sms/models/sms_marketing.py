# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.addons.ace_sms.models.esms_request import ESMSProvider
from datetime import datetime


class SmsMarketing(models.Model):
    _name = 'sms.marketing'
    _description = 'SMS Marketing'

    name = fields.Char()
    # sms_template_id = fields.Many2one('sms.template', string="Template", ondelete='cascade')
    brand_id = fields.Many2one('sms.brand', required=True, string="Brand", ondelete='cascade')
    sms_content = fields.Text(string='SMS Content')
    partner_ids = fields.Many2many('res.partner', 'sms_marketing_partner_rel', 'marketing_id', 'partner_id',
                                   string="Partners")
    # type = fields.Selection([('option', 'Options'), ('group', 'Group')], string="Type")
    group_id = fields.Many2one('sms.marketing.group', string="Group")
    sms_message_ids = fields.One2many('sms.message', 'marketing_id', string="Messages")
    state = fields.Selection([('draft', 'Draft'), ('sent', 'Sent')], default='draft')

    @api.onchange('group_id')
    def onchange_group_id(self):
        if self.group_id:
            self.partner_ids = [(4, partner.id) for partner in self.group_id.partner_ids]

    @api.multi
    def send_sms(self):
        for partner in self.partner_ids:
            if not partner.phone:
                continue
            my_sms = self.brand_id.send_message(partner.phone, self.sms_content.encode('utf-8'))

            status = self.env['sms.message.status'].get_status(self.brand_id.gateway_id.id)
            # for single smses we only record succesful sms, failed ones reopen the form with the error message
            sms_message = self.env['sms.message'].create({
                'record_id': False,
                'model_id': False,
                'brand_id': self.brand_id.id,
                'to_mobile': partner.phone,
                'sms_content': self.sms_content,
                'message_date': datetime.utcnow(),
                'status_id': status.get(my_sms.get('CodeResponse', False) or my_sms.get('CodeResult', False), False),
                'sms_gateway_message_id': my_sms.get('SMSID', my_sms.get('Exception', '')),
                'by_partner_id': self.env.user.partner_id.id,
                'marketing_id': self.id,
                'partner_id': partner.id,
            })
        self.state = 'sent'

