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


class CommissionCalculation(models.Model):
    _name = 'commission.calculation'
    _description = _('Commission Calculation')

    operator = fields.Selection([('lt', 'Less Than'), ('between', 'Between'),
                                 ('gt', 'Great Than')], string='Operator', required=True)
    type = fields.Selection([('percentage', 'Percentage'), ('fixed_amount', 'Fixed Amount')], required=True)
    achievement = fields.Float(string='Achievement (%)', digits=dp.get_precision('Commission Achievement'),
                               required=True)
    reward = fields.Float(string='Reward', digits=dp.get_precision('Commission Reward'), required=True)
    commission_schema_id = fields.Many2one('commission.schema', string='Commission Schema')