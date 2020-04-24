# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def create(self, vals):
        move_line = super(AccountMoveLine, self).create(vals)
        if move_line.move_id and move_line.move_id.stock_move_id and \
            move_line.move_id.stock_move_id.product_id.analytic_tag_ids:
            move_line.analytic_tag_ids = [(4, tag.id) for tag in move_line.move_id.stock_move_id.product_id.analytic_tag_ids]
        return move_line