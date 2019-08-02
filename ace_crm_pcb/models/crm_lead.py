# -*- coding: utf-8 -*-
# ......................................................................................................................
#  Program Name    :             
#  Task number:    :                                                                                         
#  Author          : duykhang@pcb-graphtech.com.vn                                         
#  Creation Date   : 7/11/2019                              
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
# 7/11/2019           duykhang@pcb        Initial
# ......................................................................................................................

from odoo import api, fields, models, _
import logging
from lxml import etree

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    log_last_updated = fields.Datetime(string="Log Last Updated On", compute='get_log_last_updated', store=True)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(CrmLead, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            lc_group = self.env.user.has_group('ace_crm_pcb.group_pcb_lc')
            doc = etree.XML(res['arch'])
            fields = res.get('fields')
            if lc_group and fields:
                for field in list(self._fields):
                    field_dict = fields.get(field)
                    if field != 'stage_id' and field_dict and field_dict.get('type') == 'many2one':
                        for node in doc.xpath("//field[@name='%s']" % field):
                            node.set('widget', 'selection')

                for node in doc.xpath("//field[@name='stage_id']"):
                    node.set('options', "{'clickable': '0', 'fold_field': 'fold'}")
                for node in doc.xpath("//div[@class='oe_button_box']"): # Make div unclickable
                    node.set('style', "pointer-events: none;")
                for node in doc.xpath("//header"): # Make header unclickable
                    node.set('style', "pointer-events: none;")
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res

    @api.depends('message_ids')
    def get_log_last_updated(self):
        for lead in self:
            lead.log_last_updated = lead.message_ids and lead.message_ids[0].date or False
