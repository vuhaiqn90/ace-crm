# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                name = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'sale.order') or _('New')
            else:
                name = self.env['ir.sequence'].next_by_code('sale.order') or _('New')
            if self.env.user.partner_id.ref:
                name = name.replace('MANV', self.env.user.partner_id.ref)
            vals['name'] = name
        if vals.get('default_code', False) and \
            self.search_count([('default_code', '=', vals.get('default_code', False))]) > 0:
            raise UserError(_("Product code has already existed. Please check again"))
        product_id = super(SaleOrder, self).create(vals)
        return product_id