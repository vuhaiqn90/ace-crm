# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    log_last_updated = fields.Datetime(string="Log Last Updated On", compute='get_log_last_updated', store=True)

    @api.depends('message_ids')
    def get_log_last_updated(self):
        for lead in self:
            lead.log_last_updated = lead.message_ids and lead.message_ids[0].date or False