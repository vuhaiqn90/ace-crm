# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('ref', 'parent_id')
    def _check_valid_customer(self):
        if not self.ref and not self.parent_id:
            raise ValidationError(_("Pls input code for Customer."))

    @api.multi
    def write(self, vals):
        if vals.get('ref', False) and self.search_count(
            [('ref', '=', vals.get('ref', False)), ('id', 'not in', self.ids)]) > 0:
            raise Warning(_("Customer Code already exists."))
        return super(ResPartner, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get('ref', False) and self.search_count([('ref', '=', vals.get('ref', False))]) > 0:
            raise Warning(_("Customer Code already exists."))
        partner_id = super(ResPartner, self).create(vals)
        if not partner_id.ref and not partner_id.parent_id:
            raise UserError(_("Pls insert code for Customer."))
        return partner_id

    @api.depends('is_company', 'name', 'parent_id.name', 'type', 'company_name', 'ref')
    def _compute_display_name(self):
        diff = dict(show_address=None, show_address_only=None, show_email=None)
        names = dict(self.with_context(**diff).name_get())
        for partner in self:
            partner.display_name = names.get(partner.id)

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.ref:
                name = '[' + record.ref + '] ' + (record.name or '')
            res.append((record.id, name))
        return res