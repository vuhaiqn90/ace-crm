# -*- coding: utf-8 -*-
# ......................................................................................................................
#  Program Name    :             
#  Task number:    :                                                                                         
#  Author          : duykhang@pcb-graphtech.com.vn                                         
#  Creation Date   : 12/3/2019                              
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
# 12/3/2019           duykhang@pcb        Initial
# ......................................................................................................................

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    def compute_tour_dates(self):
        for record in self:
            tour_rcs = self.env['tour.package'].search([('product_id', '=', record.id)], limit=1)
            tour_dates = self.env['tour.dates'].search([('tour_id.product_id', '=', record.id),
                                                        ('state', '=', 'available')])
            tour_programs = self.env['tour.programme'].search([('tour_id1.product_id', '=', record.id)])
            record.update({'tour_dates': [(6, 0, tour_dates.ids)],
                           'tour_program': [(6, 0, tour_programs.ids)],
                           'tour_intro': tour_rcs.tour_intro})

    _inherit = 'product.product'

    tour_dates = fields.Many2many('tour.dates', string='Tour Dates', compute='compute_tour_dates')
    tour_program = fields.Many2many('tour.programme', string='Tour Programme', compute='compute_tour_dates')
    tour_intro = fields.Text(string='Tour Intro', compute='compute_tour_dates')