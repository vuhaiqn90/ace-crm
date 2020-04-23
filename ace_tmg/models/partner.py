# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    agent_level = fields.Selection([('level_1', 'Kênh đại lý cấp 1'), ('level_2', 'Kênh đại lý cấp 2')],
                                   string='Agent Level')
    trial = fields.Boolean('Trial Work')
    job_position = fields.Selection([('sale', 'Salesperson'), ('tels', 'Telesales'), ('ctv', 'CTV')],
                                    string='Job Position')