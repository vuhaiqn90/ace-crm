# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.onchange('picking_type_id')
    def onchange_picking_type_id(self):
        if self.picking_type_id and self.state in ['confirmed', 'waiting']:
            if self.picking_type_id.default_location_src_id:
                location_id = self.picking_type_id.default_location_src_id.id
            else:
                location_id = self.env['stock.warehouse']._get_partner_locations()

            if self.picking_type_id.default_location_dest_id:
                location_dest_id = self.picking_type_id.default_location_dest_id.id
            else:
                location_dest_id = self.env['stock.warehouse']._get_partner_locations()

            if location_id:
                self.location_id = location_id
            if location_dest_id:
                self.location_dest_id = location_dest_id

    @api.multi
    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        # Change operation type of moves if those of the picking change
        after_vals = {}
        if vals.get('picking_type_id'):
            after_vals['picking_type_id'] = vals['picking_type_id']
        if after_vals:
            self.mapped('move_lines').filtered(lambda move: not move.scrapped).write(after_vals)
        return res
