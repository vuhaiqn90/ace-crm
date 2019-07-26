# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def default_get(self, fields):
        rec = super(SaleOrder, self).default_get(fields)
        if self._context.get('active_model') == 'crm.lead':
            lead_id = self.env['crm.lead'].browse(self._context.get('active_id'))
            rec.update({
                'order_line': [(0, 0, {
                    'product_id': line.product_id,
                    'name': line.name,
                    'product_uom_qty': line.product_qty,
                    'price_unit': line.price_unit,
                }) for line in lead_id.lead_line_ids]
            })
        return rec