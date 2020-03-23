# -*- coding: utf-8 -*-
# ......................................................................................................................
#  Program Name    :             
#  Task number:    :                                                                                         
#  Author          : duykhang@pcb-graphtech.com.vn                                         
#  Creation Date   : 3/3/2020                              
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
# 3/3/2020           duykhang@pcb        Initial
# ......................................................................................................................

from odoo import api, fields, models, _
import logging
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import date, datetime, timedelta
from odoo.exceptions import Warning, UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def create(self, vals):
        # Create an inactive user and remove this user from all groups
        user_rcs = self.env['res.users'].sudo(self.env.user).create(self.prepare_user_data())
        sql_remove_user_from_group = self.prepare_remove_user_from_group(user_rcs.id)
        if sql_remove_user_from_group:
            self.env.cr.execute(sql_remove_user_from_group)
        vals.update({
            'user_id': user_rcs.id if user_rcs else False
        })
        res = super(HrEmployee, self).create(vals)
        return res

    def prepare_user_data(self):
        """
        ToDo: Inherit this method to add or remove some information of user
        :return:
        """
        return {
            'name': self.name,
            'email': self.work_email,
            'phone': self.work_phone,
            'mobile': self.mobile_phone,
            'active': False
        }

    def prepare_remove_user_from_group(self, user_id):
        """
        ToDo: return False to by pass this SQL
        """
        sql = """
        delete from res_groups_users_rel where uid = %s
        """ % user_id
        return sql