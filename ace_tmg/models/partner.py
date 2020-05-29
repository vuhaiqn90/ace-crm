# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    agent_level = fields.Selection([('level_1', 'Kênh đại lý cấp 1'), ('level_2', 'Kênh đại lý cấp 2')],
                                   string='Agent Level')
    trial = fields.Boolean('Trial Work')
    job_position = fields.Selection([('sale', 'Salesperson'), ('tels', 'Telesales'), ('ctv', 'CTV')],
                                    string='Job Position')

    def _get_name(self):
        """ Utility method to allow name_get to be overrided without re-browse the partner """
        partner = self
        name = partner.ref and '[%s] %s' % (partner.ref, partner.name) or partner.name

        if partner.company_name or partner.parent_id:
            if not name and partner.type in ['invoice', 'delivery', 'other']:
                name = dict(self.fields_get(['type'])['type']['selection'])[partner.type]
            if not partner.is_company:
                name = self._get_contact_name(partner, name)
        if self._context.get('show_address_only'):
            name = partner._display_address(without_company=True)
        if self._context.get('show_address'):
            name = name + "\n" + partner._display_address(without_company=True)
        name = name.replace('\n\n', '\n')
        name = name.replace('\n\n', '\n')
        if self._context.get('address_inline'):
            name = name.replace('\n', ', ')
        if self._context.get('show_email') and partner.email:
            name = "%s <%s>" % (name, partner.email)
        if self._context.get('html_format'):
            name = name.replace('\n', '<br/>')
        if self._context.get('show_vat') and partner.vat:
            name = "%s ‒ %s" % (name, partner.vat)
        return name

    @api.multi
    def name_get(self):
        result = []
        for partner in self:
            name = partner._get_name()
            result.append((partner.id, name))
        return result