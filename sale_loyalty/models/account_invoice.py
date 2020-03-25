# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import openerp.addons.decimal_precision as dp

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        for invoice in self:
            order_id = invoice.mapped('invoice_line_ids.sale_line_ids.order_id')
            if invoice.type == 'out_invoice':
                if order_id:
                    invoice.partner_id.loyalty_points += order_id.points_won
            elif invoice.type == 'out_refund':
                if not order_id and invoice.refund_invoice_id:
                    order_id = invoice.refund_invoice_id.mapped('invoice_line_ids.sale_line_ids.order_id')
                if order_id:
                    invoice.partner_id.loyalty_points -= order_id.points_won
        return super(AccountInvoice, self).action_invoice_open()

    @api.multi
    def action_invoice_cancel(self):
        for inv in self:
            order_id = inv.mapped('invoice_line_ids.sale_line_ids.order_id')
            if order_id:
                if inv.type == 'out_invoice':
                    inv.partner_id.loyalty_points -= order_id.points_won
                elif inv.type == 'out_refund':
                    inv.partner_id.loyalty_points += order_id.points_won
        return super(AccountInvoice, self).action_invoice_cancel()