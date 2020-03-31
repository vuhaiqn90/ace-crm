# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_default_membership(self):
        membership_id = self.env['membership.level'].search([('point', '<=', 0)], order='point desc', limit=1)
        return membership_id and membership_id.id or False

    loyalty_points = fields.Float(help='The loyalty points the user won as part of a Loyalty Program')
    membership_id = fields.Many2one('membership.level', string="Membership",
                                    default=lambda self: self._get_default_membership())
    presenter = fields.Many2one('res.partner')

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        for partner in self:
            membership_id = self.env['membership.level'].search([('point', '<=', partner.loyalty_points)],
                                                                order='point desc', limit=1)
            # if membership_id and (not partner.membership_id or partner.membership_id.point < partner.loyalty_points):
            if membership_id and membership_id != partner.membership_id:
                # partner.membership_id = membership_id.id
                self._cr.execute("""UPDATE res_partner SET membership_id = %s WHERE id = %s""",
                                 (membership_id.id, partner.id))
        return res
