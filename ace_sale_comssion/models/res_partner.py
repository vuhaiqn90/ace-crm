# -*- coding: utf-8 -*-
# ......................................................................................................................
#  Program Name    :             
#  Task number:    :                                                                                         
#  Author          : duykhang@pcb-graphtech.com.vn                                         
#  Creation Date   : 2/18/2020                              
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
# 2/18/2020           duykhang@pcb        Initial
# ......................................................................................................................

from odoo import api, fields, models, _
import logging
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import date, datetime, timedelta
from odoo.exceptions import Warning, UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'


