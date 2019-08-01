# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.osv import osv
import odoo.addons.decimal_precision as dp
from lxml import etree
from odoo.osv.orm import setup_modifiers
from odoo.exceptions import Warning
import time
from odoo.tools.translate import _
from datetime import datetime, date, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_button_confirm(self):
        res = super(SaleOrder, self).action_button_confirm()
        try:
            for r in self:
                sms_compose = self.env['sms.compose'].create({
                    'record_id': r.id,
                    'model': r._name,
                    'sms_template_id': self.env.ref('ace_sms.sms_template_so_send').id,
                })
                sms_compose.send_sms()
        except:
            pass
        return res