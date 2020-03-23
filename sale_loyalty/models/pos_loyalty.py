# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class LoyaltyProgram(models.Model):
    _name = 'sale.loyalty.program'
    _description = 'Sale Loyalty Program'

    name = fields.Char(string='Loyalty Program Name', index=True, required=True, help="An internal identification for the loyalty program configuration")
    pp_currency = fields.Float(string='Points per currency', help="How many loyalty points are given to the customer by sold currency")
    pp_product = fields.Float(string='Points per product', help="How many loyalty points are given to the customer by product sold")
    pp_order = fields.Float(string='Points per order', help="How many loyalty points are given to the customer for each sale or order")
    rounding = fields.Float(string='Points Rounding', default=1, help="The loyalty point amounts are rounded to multiples of this value.")
    rule_ids = fields.One2many('sale.loyalty.rule', 'loyalty_program_id', string='Rules')
    reward_ids = fields.One2many('sale.loyalty.reward', 'loyalty_program_id', string='Rewards')


class LoyaltyRule(models.Model):
    _name = 'sale.loyalty.rule'
    _description = 'Sale Loyalty Rule'

    name = fields.Char(index=True, required=True, help="An internal identification for this loyalty program rule")
    loyalty_program_id = fields.Many2one('sale.loyalty.program', string='Loyalty Program', help='The Loyalty Program this exception belongs to')
    rule_type = fields.Selection((('product', 'Product'), ('category', 'Category')), old_name='type', required=True, default='product', help='Does this rule affects products, or a category of products ?')
    product_id = fields.Many2one('product.product', string='Target Product', help='The product affected by the rule')
    category_id = fields.Many2one('product.category', string='Target Category', help='The category affected by the rule')
    cumulative = fields.Boolean(help='The points won from this rule will be won in addition to other rules')
    pp_product = fields.Float(string='Points per product', help='How many points the product will earn per product ordered')
    pp_currency = fields.Float(string='Points per currency', help='How many points the product will earn per value sold')


class LoyaltyReward(models.Model):
    _name = 'sale.loyalty.reward'
    _description = 'Sale Loyalty Reward'

    name = fields.Char(index=True, required=True, help='An internal identification for this loyalty reward')
    loyalty_program_id = fields.Many2one('sale.loyalty.program', string='Loyalty Program',
                                         help='The Loyalty Program this reward belongs to')
    minimum_points = fields.Float(help='The minimum amount of points the customer must have to qualify for this reward')
    reward_type = fields.Selection((('gift', 'Gift'), ('discount', 'Discount'), ('resale', 'Resale')),
                                   default='discount', old_name='type', required=True, help='The type of the reward')
    gift_product_id = fields.Many2one('product.product', string='Gift Product',
                                      help='The product given as a reward')
    point_cost = fields.Float(help='The cost of the reward')
    discount_product_id = fields.Many2one('product.product', string='Discount Product',
                                          help='The product used to apply discounts')
    discount = fields.Float(help='The discount percentage')
    point_product_id = fields.Many2one('product.product', string='Point Product',
                                       help='The product that represents a point that is sold by the customer')
    discount_category_id = fields.Many2one('product.category', 'Discount Category',
                                           help='The category used to apply discounts')
    type = fields.Selection([('product', 'Product'), ('category', 'Category')])
    membership_id = fields.Many2one('membership.level', 'Membership')

    @api.constrains('reward_type', 'gift_product_id')
    def _check_gift_product(self):
        if self.filtered(lambda reward: reward.reward_type == 'gift' and not reward.gift_product_id):
            raise ValidationError(_('The gift product field is mandatory for gift rewards'))

    @api.constrains('reward_type', 'discount_product_id')
    def _check_discount_product(self):
        # if self.filtered(lambda reward: reward.reward_type == 'discount' and not reward.discount_product_id):
        #     raise ValidationError(_('The discount product field is mandatory for discount rewards'))
        return True

    @api.constrains('reward_type', 'point_product_id')
    def _check_point_product(self):
        if self.filtered(lambda reward: reward.reward_type == 'resale' and not reward.point_product_id):
            raise ValidationError(_('The point product field is mandatory for point resale rewards'))
