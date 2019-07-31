from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    loyalty_points = fields.Float(help='The loyalty points the user won as part of a Loyalty Program')
    membership_id = fields.Many2one('membership.level', string="Membership")

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        for partner in self:
            membership_id = self.env['membership.level'].search([('point', '<=', partner.loyalty_points)],
                                                                order='point desc', limit=1)
            if membership_id and (not partner.membership_id or partner.membership_id.point < partner.loyalty_points):
                partner.membership_id = membership_id.id
        return res
