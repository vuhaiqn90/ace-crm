# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    agent_level = fields.Selection([('level_1', 'Kênh đại lý cấp 1'), ('level_2', 'Kênh đại lý cấp 2')],
                                   string='Agent Level')
    trial = fields.Boolean('Trial Work')
    job_position = fields.Selection([('sale', 'Salesperson'), ('tels', 'Telesales'), ('ctv', 'CTV')],
                                    string='Job Position')
    tmg_membership_id = fields.Many2one('tmg.membership.level', 'Membership')

    @api.multi
    def get_vietnam_full_address(self):
        address = ''
        if self.street:
            address += self.street + ', '
        if self.ward_id and self.ward_id.name:
            address += self.ward_id.name + ', '
        if self.district_id and self.district_id.name:
            address += self.district_id.name + ', '
        if self.state_id and self.state_id.name:
            address += self.state_id.name + ', '
        if self.country_id and self.country_id.name:
            address += self.country_id.name + ', '
        return address.strip(', ')

    def _get_name(self):
        """ Utility method to allow name_get to be overrided without re-browse the partner """
        partner = self
        name = partner.ref and '[%s] %s' % (partner.ref, partner.name) or partner.name

        # if partner.company_name or partner.parent_id:
        #     if not name and partner.type in ['invoice', 'delivery', 'other']:
        #         name = dict(self.fields_get(['type'])['type']['selection'])[partner.type]
        #     if not partner.is_company:
        #         name = self._get_contact_name(partner, name)
        if self._context.get('show_address_only'):
            name = partner.get_vietnam_full_address()
        if self._context.get('show_address'):
            name = name + "\n" + partner.get_vietnam_full_address()
        if name:
            name = name.replace('\n\n', '\n')
            name = name.replace('\n\n', '\n')
        if self._context.get('address_inline'):
            name = name.replace('\n', ', ')
        if self._context.get('show_email') and partner.email:
            name = "%s <%s>" % (name, partner.email)
        if self._context.get('html_format'):
            name = name.replace('\n', '<br/>')
        # if self._context.get('show_vat') and partner.vat:
        #     name = "%s ‒ %s" % (name, partner.vat)
        return name

    @api.multi
    def name_get(self):
        result = []
        for partner in self:
            name = partner._get_name()
            result.append((partner.id, name))
        return result