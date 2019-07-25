# -*- coding: utf-8 -*
from datetime import datetime

from odoo import api, fields, models

class SmsCompose(models.Model):
    _name = "sms.compose"
    _description = 'SMS Compose'
    
    error_message = fields.Char(readonly=True)
    record_id = fields.Integer()
    model = fields.Char()
    sms_template_id = fields.Many2one('sms.template', string="Template", ondelete='cascade')
    brand_id = fields.Many2one('sms.brand', required=True, string="Brand", ondelete='cascade')
    to_number = fields.Char(required=True, string='To Mobile Number')
    sms_content = fields.Text(string='SMS Content')

    @api.onchange('sms_template_id')
    def _onchange_sms_template_id(self):
        """
            Prefills from mobile, sms_account and sms_content but allow them to manually change the content after
        """
        if self.sms_template_id.id != False:
            sms_rendered_content = self.env['sms.template'].render_template(self.sms_template_id.template_body, self.sms_template_id.model_id.model, self.record_id)
            sms_rendered_to_phone = self.env['sms.template'].render_template(self.sms_template_id.sms_to, self.sms_template_id.model_id.model, self.record_id)
            self.brand_id = self.sms_template_id.brand_id.id
            self.to_number = sms_rendered_to_phone
            self.sms_content = sms_rendered_content

    @api.multi
    def send_sms(self):
        """
            Attempt to send the sms, if any error comes back show it to the user and only log the smses that successfully sent
        """
        self.ensure_one()

        my_sms = self.brand_id.send_message(self.to_number, self.sms_content.encode('utf-8'), self.model, self.record_id)

        model = self.env['ir.model'].search([('model','=',self.model)])
        status = self.env['sms.message.status'].get_status(self.brand_id.gateway_id.id)
        #for single smses we only record succesful sms, failed ones reopen the form with the error message
        sms_message = self.env['sms.message'].create({
            'record_id': self.record_id,
            'model_id': model[0].id if model and len(model) > 0 else False,
            'brand_id': self.brand_id.id,
            'to_mobile': self.to_number,
            'sms_content': self.sms_content,
            'message_date': datetime.utcnow(),
            'status_id': status.get(my_sms.get('CodeResponse', False) or my_sms.get('CodeResult', False) , False),
            'sms_gateway_message_id': my_sms.get('SMSID', my_sms.get('Exception', '')),
            'by_partner_id': self.env.user.partner_id.id
        })

        try:
            discussion_subtype = self.env['ir.model.data'].get_object('mail', 'mt_comment')
            self.env[self.model].search([('id','=', self.record_id)]).message_post(body=self.sms_content,
                                                                                   subject="SMS Sent",
                                                                                   type="comment",
                                                                                   subtype_id=discussion_subtype.id)
        except:
            #Message post only works if CRM module is installed
            pass
        return True

    @api.model
    def _prepare_add_missing_fields(self, values):
        """ Deduce missing required fields from the onchange """
        res = {}
        onchange_fields = ['brand_id', 'to_number', 'sms_content']
        if values.get('sms_template_id', False) and any(f not in values for f in onchange_fields):
            sms_compose = self.new(values)
            sms_compose._onchange_sms_template_id()
            for field in onchange_fields:
                if field not in values:
                    res[field] = sms_compose._fields[field].convert_to_write(sms_compose[field], sms_compose)
        return res

    @api.model
    def create(self, values):
        values.update(self._prepare_add_missing_fields(values))
        res = super(SmsCompose, self).create(values)
        return res
