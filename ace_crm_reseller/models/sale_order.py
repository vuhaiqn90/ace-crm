# -*- coding: utf-8 -*-
# ......................................................................................................................
#  Program Name    :             
#  Task number:    :                                                                                         
#  Author          : duykhang@pcb-graphtech.com.vn                                         
#  Creation Date   : 7/2/2019                              
#  Reference:      :                      
#  Logical Database:                                              
# ......................................................................................................................
#  
# ......................................................................................................................
#  External References:                                            
# ......................................................................................................................
#  Technical Requirements:                                        
# ......................................................................................................................
#  Modifications:                                                      
#                                                                      
#  Date             Developer            Modification                              
# ...................................................................................................................... 
# 7/2/2019           duykhang@pcb        Initial
# ......................................................................................................................

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    @api.depends('reseller_op_id')
    def compute_opportunity(self):
        for sale in self:
            if sale.reseller_op_id:
                sale.update({'opportunity_id': sale.reseller_op_id.parent_id.id})
            else:
                opportunity_id = self.env.context.get('default_opportunity_id', False)
                if opportunity_id:
                    sale.update({'opportunity_id': opportunity_id})

    _inherit = 'sale.order'

    reseller_op_id = fields.Many2one('ace.opportunity.reseller', 'Reseller')
    opportunity_id = fields.Many2one('crm.lead', string='Opportunity', domain="[('type', '=', 'opportunity')]",
                                     compute="compute_opportunity", store=True)
    primary = fields.Boolean()

    @api.onchange('primary')
    def onchange_primary(self):
        if not self.primary and self._origin.primary:
            warning = {}
            title = _("Warning for %s") % self.name
            message = "Can't uncheck Primary."
            warning['title'] = title
            warning['message'] = message
            self.primary = self._origin.primary
            return {'warning': warning}

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        if order.primary:
            if order.reseller_op_id:
                order.reseller_op_id.planned_revenue = order.amount_total
                if order.reseller_op_id.parent_id:
                    order.reseller_op_id.parent_id.planned_revenue = order.amount_total
                other_quotation_ids = self.env['sale.order'].sudo().search([
                    ('reseller_op_id', '=', order.reseller_op_id.id),
                    ('primary', '=', True),
                    ('id', '!=', order.id)
                ])
                if other_quotation_ids:
                    other_quotation_ids.primary = False
            if order.opportunity_id:
                order.opportunity_id.planned_revenue = order.amount_total
                other_quotation_ids = self.env['sale.order'].sudo().search([
                    ('opportunity_id', '=', order.opportunity_id.id),
                    ('primary', '=', True),
                    ('id', '!=', order.id)
                ])
                if other_quotation_ids:
                    other_quotation_ids.primary = False
        return order

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        for order in self:
            if 'primary' in vals and order.primary:
                if order.state == 'cancel':
                    if order.reseller_op_id:
                        order.reseller_op_id.planned_revenue = 0
                        if order.reseller_op_id.parent_id:
                            order.reseller_op_id.parent_id.planned_revenue = 0
                    if order.opportunity_id:
                        order.opportunity_id.planned_revenue = 0
                else:
                    if order.reseller_op_id:
                        order.reseller_op_id.planned_revenue = order.amount_total
                        if order.reseller_op_id.parent_id:
                            order.reseller_op_id.parent_id.planned_revenue = order.amount_total
                    if order.opportunity_id:
                        order.opportunity_id.planned_revenue = order.amount_total
                if order.reseller_op_id:
                    other_quotation_ids = self.env['sale.order'].sudo().search([
                        ('reseller_op_id', '=', order.reseller_op_id.id),
                        ('primary', '=', True),
                        ('id', '!=', order.id)
                    ])
                    if other_quotation_ids:
                        other_quotation_ids.primary = False
                if order.opportunity_id:
                    other_quotation_ids = self.env['sale.order'].sudo().search([
                        ('opportunity_id', '=', order.opportunity_id.id),
                        ('primary', '=', True),
                        ('id', '!=', order.id)
                    ])
                    if other_quotation_ids:
                        other_quotation_ids.primary = False
        return res

    @api.multi
    def action_cancel(self):
        for order in self:
            if order.primary:
                if order.reseller_op_id:
                    order.reseller_op_id.planned_revenue = 0
                    if order.reseller_op_id.parent_id:
                        order.reseller_op_id.parent_id.planned_revenue = 0
                if order.opportunity_id:
                    order.opportunity_id.planned_revenue = 0
        return super(SaleOrder, self).action_cancel()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def create(self, vals):
        line = super(SaleOrderLine, self).create(vals)
        order = line.order_id
        if order.primary:
            if order.reseller_op_id:
                order.reseller_op_id.planned_revenue = order.amount_total
                if order.reseller_op_id.parent_id:
                    order.reseller_op_id.parent_id.planned_revenue = order.amount_total
            if order.opportunity_id:
                order.opportunity_id.planned_revenue = order.amount_total
        return line

    @api.multi
    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        for line in self:
            order = line.order_id
            if ('product_uom_qty' in vals or 'price_unit' in vals or 'tax_id' in vals) and order.primary:
                if order.reseller_op_id:
                    order.reseller_op_id.planned_revenue = order.amount_total
                    if order.reseller_op_id.parent_id:
                        order.reseller_op_id.parent_id.planned_revenue = order.amount_total
                if order.opportunity_id:
                    order.opportunity_id.planned_revenue = order.amount_total
        return res