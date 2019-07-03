# -*- coding: utf-8 -*-
# ......................................................................................................................
#  Program Name    :             
#  Task number:    : T0135
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


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    reseller_lines = fields.One2many('ace.opportunity.reseller', 'parent_id', string='Reseller List')

    @api.multi
    def action_schedule_meeting(self):
        res = super(CrmLead, self).action_schedule_meeting()
        res['context'].update({
            'search_default_opportunity_id': self.id,
        })
        return res