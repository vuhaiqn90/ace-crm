# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    tmg_price_unit = fields.Float(string='Price without Discount', digits=dp.get_precision('Product Price'))
    tmg_discount = fields.Float(string='Discount', digits=dp.get_precision('Discount'))

    @api.onchange('tmg_price_unit', 'tmg_discount', 'product_qty')
    def tmg_get_price_unit(self):
        if self.tmg_price_unit or self.tmg_discount:
            price_subtotal = self.product_qty * self.tmg_price_unit - \
                             self.product_qty * self.tmg_price_unit * self.tmg_discount / 100
            self.price_unit = price_subtotal / self.product_qty