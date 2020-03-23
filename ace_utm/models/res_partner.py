# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ['res.partner', 'utm.mixin']