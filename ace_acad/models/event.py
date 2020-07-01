# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    companyname = fields.Char(string='Company Name')