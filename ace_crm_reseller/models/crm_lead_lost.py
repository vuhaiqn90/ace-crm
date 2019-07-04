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
            resellers.parent_id.write({'lost_reason': self.lost_reason_id.id})
            resellers.parent_id.action_set_lost()
            resellers.action_set_lost()
            resellers.write({'lost_reason': self.lost_reason_id.id, 'active': True})
            return True
        res = super(CrmLeadLost, self).action_lost_reason_apply()
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        for lead in leads:
            for reseller in lead.reseller_lines:
                reseller.write({'lost_reason': self.lost_reason_id.id})
                reseller.action_set_lost()
        return res
