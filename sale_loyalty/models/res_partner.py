from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    loyalty_points = fields.Float(help='The loyalty points the user won as part of a Loyalty Program')
