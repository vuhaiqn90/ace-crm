# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange('product_id')
    def get_analytic_tags(self):
        if self.product_id and self.product_id.analytic_tag_ids:
            self.analytic_tag_ids = [(4, tag.id) for tag in self.product_id.analytic_tag_ids]

    @api.model
    def create(self, vals):
        invoice_line_id = super(AccountInvoiceLine, self).create(vals)
        if invoice_line_id.product_id and invoice_line_id.product_id.analytic_tag_ids:
            invoice_line_id.write({'analytic_tag_ids': [(4, tag.id) for tag in invoice_line_id.product_id.analytic_tag_ids]})
        return invoice_line_id