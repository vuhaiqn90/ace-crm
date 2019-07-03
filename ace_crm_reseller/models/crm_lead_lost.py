# -*- coding: utf-8 -*-
# ......................................................................................................................
#  Program Name    :             
#  Task number:    :                                                                                         
#  Author          : duykhang@pcb-graphtech.com.vn                                         
#  Creation Date   : 7/3/2019                              
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
# 7/3/2019           duykhang@pcb        Initial
# ......................................................................................................................

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class CrmLeadLost(models.TransientModel):
    _inherit = 'crm.lead.lost'

    @api.multi
    def action_lost_reason_apply(self):
        if self.env.context.get('active_model', False) == 'ace.opportunity.reseller':
            resellers = self.env['ace.opportunity.reseller'].browse(self.env.context.get('active_ids'))
            resellers.write({'lost_reason': self.lost_reason_id.id})
            resellers.parent_id.write({'lost_reason': self.lost_reason_id.id})
            resellers.parent_id.action_set_lost()
            return resellers.action_set_lost()
        return super(CrmLeadLost, self).action_lost_reason_apply()
