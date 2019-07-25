# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    loyalty_id = fields.Many2one('sale.loyalty.program', 'Loyalty Program', help='Set Loyalty Program on sale order')

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('res.config.settings', "loyalty_id", self.loyalty_id.id)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        loyalty_id = IrDefault.get('res.config.settings', "loyalty_id")
        res.update(loyalty_id=loyalty_id if loyalty_id else False)
        return res
