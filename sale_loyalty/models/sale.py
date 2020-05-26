# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import openerp.addons.decimal_precision as dp

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('partner_id', 'order_line')
    def _get_points_total(self):
        for order in self:
            points_total = order.partner_id.loyalty_points + order.points_won
            order.points_total = points_total

    # @api.multi
    # def action_confirm(self):
    #     for order in self:
    #         order.partner_id.loyalty_points = order.partner_id.loyalty_points + order.points_won
    #     res = super(SaleOrder, self).action_confirm()
    #     return res

    @api.depends('order_line', 'order_line.price_subtotal')
    def _get_point_won(self):
        loyalty_id = self.env['ir.default'].sudo().get('res.config.settings', "loyalty_id")
        loyalty = self.env['sale.loyalty.program'].browse(loyalty_id)

        for order in self:
            if order.order_line:
                reward_line = order.mapped('order_line').filtered(lambda l: l.price_subtotal < 0)
                if not reward_line and order.points_spent < 0:
                    order.points_total = order.points_total - order.points_spent
                    order.points_spent = 0.00
                points = loyalty.pp_order
            else:
                points = 0.00

            if not loyalty.rule_ids:
                if loyalty.pp_currency:
                    points += round(order.amount_total) / loyalty.pp_currency
                if loyalty.pp_product:
                    total_point = sum(order.mapped('order_line').mapped('product_uom_qty')) / loyalty.pp_product
                    points += total_point
                order.points_won = points
            else:
                # for rule in loyalty.rule_ids.filtered(lambda x: x.rule_type == 'product'):
                for rule in loyalty.rule_ids:
                    if rule.rule_type == 'product':
                        lines = order.mapped('order_line').filtered(lambda l: l.product_id == rule.product_id)
                    else:
                        category_ids = self.env['product.category'].search([('id', 'child_of', rule.category_id.id)])
                        lines = order.mapped('order_line').filtered(lambda l: l.product_id.categ_id in category_ids)
                    if rule.pp_product and not rule.cumulative:
                        total_qty = sum(lines.mapped('product_uom_qty'))
                        points += (total_qty / rule.pp_product)
                    if rule.pp_currency and not rule.cumulative:
                        total_price = sum(lines.mapped('price_subtotal'))
                        points += (total_price / rule.pp_currency)
                    if rule.cumulative:
                        total_qty = sum(lines.mapped('product_uom_qty'))
                        total_price = sum(lines.mapped('price_subtotal'))

                        pp_product_point = total_qty / rule.pp_product

                        if rule.pp_currency:
                            pp_currency_point = total_price / rule.pp_currency
                        else:
                            pp_currency_point = total_price / loyalty.pp_currency
                        points += (pp_currency_point + pp_product_point)
                    order.points_won = points

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        if self.partner_id:
            values = {}
            values['points_total'] = self.partner_id.loyalty_points
            values['temp_points_total'] = self.partner_id.loyalty_points
            self.update(values)

    @api.depends('run_loyalty_reward', 'order_line.discount')
    def check_hide_button_reward(self):
        for order in self:
            order.hide_button_reward = False
            if order.run_loyalty_reward and any(line.discount > 0 for line in order.order_line):
                order.hide_button_reward = True

    # Fields
    temp_points_won = fields.Float(string="Temp Won Points", digits=dp.get_precision('Product Price'), store=True)
    temp_points_total = fields.Float(string="Temp Total Points", digits=dp.get_precision('Product Price'), store=True)
    points_won = fields.Float(string="Won Points", compute='_get_point_won', digits=dp.get_precision('Product Price'), store=True)
    points_spent = fields.Float(string="Spent Points", digits=dp.get_precision('Product Price'))
    points_total = fields.Float(string="Total Points", compute='_get_points_total', digits=dp.get_precision('Product Price'), store=True)
    membership_id = fields.Many2one('membership.level', string="Membership", related='partner_id.membership_id')
    loyalty_points = fields.Float('Loyalty Points', related='partner_id.loyalty_points')
    run_loyalty_reward = fields.Boolean('Run Loyalty Reward')
    hide_button_reward = fields.Boolean(compute='check_hide_button_reward')

    @api.multi
    def button_reward(self):
        loyalty_id = self.env['ir.default'].sudo().get('res.config.settings', "loyalty_id")
        loyalty = self.env['sale.loyalty.program'].browse(loyalty_id)
        SoLine = self.env['sale.order.line']
        # temp_points_won = self.points_won
        start_membership = self.env['membership.level'].search([('point', '<=', 0)], order='point desc', limit=1)
        for reward in loyalty.reward_ids:
            # self.points_spent = self.points_spent * -1
            # if self.points_total >= reward.minimum_points:
                if reward.reward_type == 'gift':
                    SoLine.create({
                        'product_id': reward.gift_product_id.id,
                        'product_uom_qty': 1.0,
                        'price_unit': 0.0,
                        'order_id': self.id
                    })
                    self.run_loyalty_reward = True
                    # self.points_total = self.points_total - reward.point_cost
                    # self.partner_id.loyalty_points = self.partner_id.loyalty_points - reward.point_cost
                    # self.points_spent += reward.point_cost
                elif reward.reward_type == 'discount':
                    # total_price = self.amount_untaxed
                    # discount = -(total_price * (reward.discount / 100))
                    # if discount >= total_price:
                    #     discount = -total_price
                    # SoLine.create({'product_id': reward.discount_product_id.id, 'product_uom_qty': 1.0, 'price_unit': discount, 'order_id': self.id})
                    if reward.type == 'product':
                        order_line_ids = self.order_line.filtered(
                            lambda l: (not reward.discount_product_id or l.product_id == reward.discount_product_id) and
                                      (not reward.membership_id or (l.order_id.partner_id.membership_id or start_membership) == reward.membership_id))
                    else:
                        category_ids = self.env['product.category'].search([('id', 'child_of', reward.discount_category_id.id)])
                        order_line_ids = self.order_line.filtered(
                            lambda l: (not reward.discount_category_id or l.product_id.categ_id in category_ids) and
                                      (not reward.membership_id or (l.order_id.partner_id.membership_id or start_membership) == reward.membership_id))
                    # order_line_ids.write({'discount': reward.discount})
                    for line in order_line_ids:
                        line.discount = line.discount + reward.discount
                        if reward.analytic_tag_ids:
                            line.analytic_tag_ids = [(4, tag.id) for tag in reward.analytic_tag_ids]
                    if order_line_ids:
                        self.run_loyalty_reward = True
                    # self.points_total -= reward.point_cost
                    # self.partner_id.loyalty_points -= reward.point_cost
                    # self.points_spent -= reward.point_cost
                # elif reward.reward_type == 'resale':
                #     total_qty = sum(self.mapped('order_line').filtered(lambda l: l.product_id == reward.point_product_id).mapped('product_uom_qty'))
                #     if total_qty <= self.points_total:
                #         price = -reward.point_product_id.lst_price
                #         SoLine.create({
                #             'product_id': reward.discount_product_id.id,
                #             'product_uom_qty': total_qty,
                #             'price_unit': price,
                #             'order_id': self.id
                #         })
                #         # self.points_total = self.points_total - total_qty
                #         # self.partner_id.loyalty_points = self.partner_id.loyalty_points - total_qty
                #         # self.points_spent += reward.point_product_id.lst_price
                #     else:
                #         price = -reward.point_product_id.lst_price
                #         SoLine.create({
                #             'product_id': reward.discount_product_id.id,
                #             'product_uom_qty': self.points_total,
                #             'price_unit': price,
                #             'order_id': self.id
                #         })
                #         # self.points_total = self.partner_id.loyalty_points = 0.00
                #         # self.points_spent += reward.point_product_id.lst_price
            # else:
            #     raise UserError(_('There are no rewards available for this customer as part of the loyalty program'))
        # self.temp_points_total = self.points_total
        # self.points_spent = self.points_spent * -1
        # self.points_won = temp_points_won
