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
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class CommissionSchema(models.Model):
    _name = 'commission.schema'
    _description = _('Commission Calculation')

    name = fields.Char(string='Commission Number')
    note = fields.Text(string='Notes')
    active = fields.Boolean(string='Active')
    calculation_lines = fields.One2many('commission.calculation', 'commission_schema_id', string='Settings')


