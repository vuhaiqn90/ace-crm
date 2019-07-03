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