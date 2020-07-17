# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # @api.depends('sale_id', 'sale_id.order_line', 'sale_id.order_line.analytic_tag_ids')
    def check_wine_to_try(self):
        for pick in self:
            analytic_tags = pick.mapped('sale_id.order_line.analytic_tag_ids')
            if analytic_tags and any(tag.name == 'Rượu thử' for tag in analytic_tags):
                self.wine_to_try = True
            else:
                self.wine_to_try = False

    receiver_deliver = fields.Char('Receiver/Deliver')
    mobile = fields.Char('Receiver/Deliver Mobile')
    address = fields.Char('Receiver/Deliver Address')
    wine_to_try = fields.Boolean(string='Wine to try', compute='check_wine_to_try')

    @api.model
    def default_get(self, fields):
        res = super(StockPicking, self).default_get(fields)
        if res.get('partner_id'):
            parter_id = self.env['res.partner'].browse(res.get('partner_id'))
            res.update({'address': parter_id.vietnam_full_address or ''})
        return res

    @api.onchange('partner_id')
    def get_default_address(self):
        if self.partner_id:
            self.address = self.partner_id.vietnam_full_address or ''

    @api.onchange('picking_type_id')
    def onchange_picking_type_id(self):
        if self.picking_type_id and self.state in ['confirmed', 'waiting']:
            if self.picking_type_id.default_location_src_id:
                location_id = self.picking_type_id.default_location_src_id.id
            else:
                customerloc, location_id = self.env['stock.warehouse']._get_partner_locations()

            if self.picking_type_id.default_location_dest_id:
                location_dest_id = self.picking_type_id.default_location_dest_id.id
            else:
                location_dest_id, supplierloc = self.env['stock.warehouse']._get_partner_locations()

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

    @api.model
    def get_text(self, report, code):
        report_id = self.env.ref(report)
        text_id = report_id and self.env['report.text.config'].search([
            ('report', '=', report_id.id),
            ('code', '=', code)
        ], limit=1) or False
        return text_id and text_id.name or ''