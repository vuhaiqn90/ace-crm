# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import openerp.addons.decimal_precision as dp
from datetime import datetime


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        for invoice in self:
            if invoice.type == 'out_invoice':
                order_id = invoice.mapped('invoice_line_ids.sale_line_ids.order_id')
                if order_id.partner_id.presenter:
                    first_order = self.env['account.invoice'].sudo().search_count([
                        ('partner_id', '=', invoice.partner_id.id),
                        ('date_invoice', '<=', invoice.date_invoice or datetime.now().date()),
                        ('type', '=', 'out_invoice'),
                        ('id', '!=', invoice.id),
                        ('state', 'in', ['open', 'in_payment', 'paid'])
                    ])
                    if not first_order:
                        membership_id = invoice.partner_id.presenter.membership_id
                        if not membership_id:
                            membership_id = self.env['membership.level'].search([('point', '<=', 0)],
                                                                                order='point desc', limit=1)
                        if membership_id and membership_id.referring_percent:
                            invoice.partner_id.presenter.loyalty_points += invoice.partner_id.presenter.membership_id.referring_percent * order_id.points_won / 100
                if order_id:
                    invoice.partner_id.loyalty_points += order_id.points_won
            elif invoice.type == 'out_refund' and invoice.refund_invoice_id:
                order_id = invoice.refund_invoice_id.mapped('invoice_line_ids.sale_line_ids.order_id')
                if order_id.partner_id.presenter:
                    first_order = self.env['account.invoice'].sudo().search_count([
                        ('partner_id', '=', invoice.partner_id.id),
                        ('date_invoice', '<=', invoice.date_invoice or datetime.now().date()),
                        ('type', '=', 'out_invoice'),
                        ('id', '!=', invoice.refund_invoice_id.id),
                        ('state', 'in', ['open', 'in_payment', 'paid'])
                    ])
                    if not first_order:
                        membership_id = invoice.partner_id.presenter.membership_id
                        if not membership_id:
                            membership_id = self.env['membership.level'].search([('point', '<=', 0)],
                                                                                order='point desc', limit=1)
                        if membership_id:
                            invoice.partner_id.presenter.loyalty_points -= invoice.partner_id.presenter.membership_id.referring_percent * order_id.points_won / 100
                if order_id:
                    invoice.partner_id.loyalty_points -= order_id.points_won
        return super(AccountInvoice, self).action_invoice_open()

    @api.multi
    def action_invoice_cancel(self):
        for inv in self:
            if inv.type == 'out_invoice':
                order_id = inv.mapped('invoice_line_ids.sale_line_ids.order_id')
                if order_id.partner_id.presenter:
                    first_order = self.env['account.invoice'].sudo().search_count([
                        ('partner_id', '=', inv.partner_id.id),
                        ('date_invoice', '<=', inv.date_invoice or datetime.now().date()),
                        ('type', '=', 'out_invoice'),
                        ('id', '!=', inv.id),
                        ('state', 'in', ['open', 'in_payment', 'paid'])
                    ])
                    if not first_order:
                        membership_id = inv.partner_id.presenter.membership_id
                        if not membership_id:
                            membership_id = self.env['membership.level'].search([('point', '<=', 0)],
                                                                                order='point desc', limit=1)
                        if membership_id:
                            inv.partner_id.presenter.loyalty_points -= inv.partner_id.presenter.membership_id.referring_percent * order_id.points_won / 100
                if order_id:
                    inv.partner_id.loyalty_points -= order_id.points_won
            elif inv.type == 'out_refund' and inv.refund_invoice_id:
                order_id = inv.refund_invoice_id.mapped('invoice_line_ids.sale_line_ids.order_id')
                if order_id.partner_id.presenter:
                    first_order = self.env['account.invoice'].sudo().search_count([
                        ('partner_id', '=', inv.partner_id.id),
                        ('date_invoice', '<=', inv.date_invoice or datetime.now().date()),
                        ('type', '=', 'out_invoice'),
                        ('id', '!=', inv.refund_invoice_id.id),
                        ('state', 'in', ['open', 'in_payment', 'paid'])
                    ])
                    if not first_order:
                        membership_id = inv.partner_id.presenter.membership_id
                        if not membership_id:
                            membership_id = self.env['membership.level'].search([('point', '<=', 0)],
                                                                                order='point desc', limit=1)
                        if membership_id:
                            inv.partner_id.presenter.loyalty_points += inv.partner_id.presenter.membership_id.referring_percent * order_id.points_won / 100
                if order_id:
                    inv.partner_id.loyalty_points += order_id.points_won
        return super(AccountInvoice, self).action_invoice_cancel()