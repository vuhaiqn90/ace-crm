# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from datetime import datetime


class SaleReturnWizard(models.TransientModel):
    _name = 'sale.return.wizard'

    reason = fields.Char()
    line_ids = fields.One2many('sale.return.wizard.line', 'wizard_id', string='Detail')

    @api.model
    def default_get(self, fields):
        res = super(SaleReturnWizard, self).default_get(fields)
        order_id = self.env[self._context.get('active_model')].browse(self._context.get('active_id'))
        if all(p.state != 'done' for p in order_id.picking_ids):
            raise Warning(_("Đơn hàng chưa xuất kho. Bạn không thể trả hàng."))
        res.update({
            'line_ids': [(0, 0, {
                'product_id': line.product_id.id,
                'uom_id': line.product_uom.id,
                'qty': line.product_uom_qty,
                'price_unit': line.price_unit,
                'total': line.product_uom_qty * line.price_unit,
            }) for line in order_id.order_line]
        })
        return res

    def action_print(self):
        order_id = self.env[self._context.get('active_model')].browse(self._context.get('active_id'))
        return self.env.ref('ace_tmg.ace_sale_return_template_py3o').with_context(
            current_date=[datetime.now().day, datetime.now().month, datetime.now().year],
            customer=order_id.partner_id.name,
            customer_company=order_id.partner_id.parent_id and order_id.partner_id.parent_id.name or '',
            return_to=order_id.warehouse_id.name,
            count_date=(datetime.now() - order_id.date_order).days,
            total_return=self.line_ids and sum(l.total for l in self.line_ids) or 0,
        ).report_action(self)


class SaleReturnWizardLine(models.TransientModel):
    _name = 'sale.return.wizard.line'

    wizard_id = fields.Many2one('sale.return.wizard')
    product_id = fields.Many2one('product.product', string='Product')
    qty = fields.Float(string='Quantity')
    uom_id = fields.Many2one('uom.uom', string='UOM')
    price_unit = fields.Float(string='Price Unit')
    total = fields.Float()

    @api.onchange('qty', 'price_unit')
    def compute_total(self):
        self.total = self.qty * self.price_unit