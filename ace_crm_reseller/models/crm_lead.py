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

    # To Do: Update Reseller From Opportunity
    # @api.multi
    # def action_set_won_rainbowman(self):
    #     res = super(CrmLead, self).action_set_won_rainbowman()
    #     for reseller in self.reseller_lines:
    #         reseller.with_context({'run_from_parent': True}).action_set_won_rainbowman()
    #     return res
    #
    # @api.multi
    # def toggle_active(self):
    #     res = super(CrmLead, self).toggle_active()
    #     for reseller in self.search(['|', ('active', '=', False), ('active', '=', True)]):
    #         reseller.with_context({'run_from_parent': True}).toggle_active()
    #     return res