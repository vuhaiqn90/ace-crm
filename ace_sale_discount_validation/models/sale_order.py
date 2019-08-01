# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[('waiting', 'Waiting Approval'), ('approved', 'Approved')])
    can_approve = fields.Boolean(compute='check_can_approve')

    def check_can_approve(self):
        for order in self:
            order.can_approve = False
            if order.order_line:
                discount = sum(l.product_uom_qty * l.price_unit * l.discount / 100 for l in order.order_line)
                subtotal = sum(l.product_uom_qty * l.price_unit for l in order.order_line)
                rate = discount / (subtotal or 1) * 100
                rate_id = self.env['ace.rate.discount'].search([('rate', '>=', rate)], order='rate', limit=1)
                if not rate_id or self.env.user in rate_id.user_ids or self.user_id in rate_id.user_ids:
                    order.can_approve = True

    @api.multi
    def send_to_approval(self):
        discount = sum(l.product_uom_qty * l.price_unit * l.discount / 100 for l in self.order_line)
        subtotal = sum(l.product_uom_qty * l.price_unit for l in self.order_line)
        rate = discount / (subtotal or 1) * 100
        rate_id = self.env['ace.rate.discount'].search([('rate', '>=', rate)], order='rate', limit=1)
        if not rate_id:
            self.write({'state': 'approved'})
            return True
        if self.env.user in rate_id.user_ids or self.user_id in rate_id.user_ids:
            self.write({'state': 'approved'})
            return True
        body_html = u'<p>Dear,</p><p>You have an order to approval.</p>' \
                    u'<p>Order information:</p>' \
                    u'<li>Order: {}</p>' \
                    u'<li>Customer: {}</p>' \
                    u'<li>Salesperson: {}</li>' \
                    u'<li>Discount: {}</li>' \
                    u'<li>Total: {}</li>'.format(self.name, self.partner_id.name,
                                                 self.user_id and self.user_id.name or '',
                                                 discount, self.amount_total)
        parameters = self.env['ir.config_parameter'].search([('key', '=', 'web.base.url')])
        url = '{}/web?#id={}&view_type=form&model=sale.order'.format(parameters.value, self.id)
        view_order = u'<p><a href="{}"><strong>View Order</strong></a></p>'.format(url)
        self.message_post(
            body=body_html + view_order,
            partner_ids=[(4, user.partner_id.id) for user in rate_id.user_ids],
            subtype='mail.mt_comment',
            notif_layout='mail.mail_notification_light',
        )
        self.write({'state': 'waiting'})

    @api.multi
    def action_approved(self):
        if any(order.state != 'waiting' for order in self):
            raise UserError(_("Order status must be Waiting Approval"))
        self.write({'state': 'approved'})