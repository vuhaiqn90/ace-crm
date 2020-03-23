# -*- coding: utf-8 -*-
# ......................................................................................................................
#  Program Name    :             
#  Task number:    :                                                                                         
#  Author          : duykhang@pcb-graphtech.com.vn                                         
#  Creation Date   : 3/16/2020                              
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
# 3/16/2020           duykhang@pcb        Initial
# ......................................................................................................................

from odoo import api, fields, models, _
import logging
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import date, datetime, timedelta
from odoo.exceptions import Warning, UserError, ValidationError

_logger = logging.getLogger(__name__)

class MailMassMailing(models.Model):
    _inherit = 'mail.mass_mailing'

    @api.onchange('mailing_model_id', 'contact_list_ids')
    def _onchange_model_and_list(self):
        mailing_domain = []
        if self.mailing_model_name:
            if self.mailing_model_name == 'mail.mass_mailing.list':
                if self.contact_list_ids:
                    mailing_domain.append(('list_ids', 'child_of', self.contact_list_ids.ids))
                else:
                    mailing_domain.append((0, '=', 1))
            elif self.mailing_model_name == 'res.partner':
                mailing_domain.append(('customer', '=', True))
            elif 'opt_out' in self.env[self.mailing_model_name]._fields and not self.mailing_domain:
                mailing_domain.append(('opt_out', '=', False))
        else:
            mailing_domain.append((0, '=', 1))
        self.mailing_domain = repr(mailing_domain)
        self.body_html = "on_change_model_and_list"


class MailMassMailing(models.Model):
    _inherit = 'mail.mass_mailing.list'

    parent_id = fields.Many2one('mail.mass_mailing.list', string='Parent')
