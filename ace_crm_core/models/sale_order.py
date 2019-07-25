# -*- coding: utf-8 -*-
# ......................................................................................................................
#  Program Name    :             
#  Task number:    :                                                                                         
#  Author          : duykhang@pcb-graphtech.com.vn                                         
#  Creation Date   : 7/25/2019                              
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
# 7/25/2019           duykhang@pcb        Initial
# ......................................................................................................................

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    @api.depends('state', 'order_line.invoice_status', 'order_line.invoice_lines')
    def _get_invoiced_amount(self):
        for so in self:
            total = sum([so.amount_total for line in so.invoice_ids])
            so.update({
                'invoiced_amount': total
            })

    _inherit = 'sale.order'

    invoice_count = fields.Integer(string='Invoice Count', compute='_get_invoiced', readonly=True, store=True)
    invoice_ids = fields.Many2many("account.invoice", string='Invoices', compute="_get_invoiced", readonly=True,
                                   copy=False, store=True)
    invoiced_amount = fields.Float(string='Invoiced Amount', compute='_get_invoiced_amount', store=True)
