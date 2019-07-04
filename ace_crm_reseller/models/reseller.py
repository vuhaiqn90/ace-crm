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


class AceOpportunityReseller(models.Model):
    @api.multi
    def _compute_phonecall_count(self):
        """Calculate number of phonecalls."""
        for lead in self:
            lead.phonecall_count = self.env[
                'crm.phonecall'].search_count(
                [('reseller_op_id', '=', lead.id)])

    @api.depends('order_ids')
    def _compute_sale_amount_total(self):
        for lead in self:
            total = 0.0
            nbr = 0
            company_currency = lead.company_currency or self.env.user.company_id.currency_id
            for order in lead.order_ids:
                if order.state in ('draft', 'sent'):
                    nbr += 1
                if order.state not in ('draft', 'sent', 'cancel'):
                    total += order.currency_id._convert(
                        order.amount_untaxed, company_currency, order.company_id,
                        order.date_order or fields.Date.today())
            lead.sale_amount_total = total
            lead.sale_number = nbr

    @api.multi
    def _compute_meeting_count(self):
        meeting_data = self.env['calendar.event'].read_group([('reseller_op_id', 'in', self.ids)], ['reseller_op_id'],
                                                             ['reseller_op_id'])
        mapped_data = {m['reseller_op_id'][0]: m['reseller_op_id_count'] for m in meeting_data}
        for lead in self:
            lead.meeting_count = mapped_data.get(lead.id, 0)

    _name = 'ace.opportunity.reseller'
    _inherit = 'crm.lead'

    partner_id = fields.Many2one('res.partner', string='Reseller Name')
    parent_id = fields.Many2one('crm.lead', string='Opportunity', ondelete='cascade')
    sale_amount_total = fields.Monetary(compute='_compute_sale_amount_total', string="Sum of Orders",
                                        help="Untaxed Total of Confirmed Orders", currency_field='company_currency')
    sale_number = fields.Integer(compute='_compute_sale_amount_total', string="Number of Quotations")
    phonecall_count = fields.Integer(
        compute='_compute_phonecall_count',
    )
    order_ids = fields.One2many('sale.order', 'reseller_op_id', string='Orders')
    meeting_count = fields.Integer('# Meetings', compute='_compute_meeting_count')
    tag_ids = fields.Many2many('crm.lead.tag', 'crm_reseller_tag_rel', 'reseller_id', 'tag_id', string='Tags',
                               help="Classify and analyze your lead/opportunity categories like: Training, Service")

    @api.model
    def default_get(self, fields):
        res = super(AceOpportunityReseller, self).default_get(fields)
        return res

    @api.multi
    def action_schedule_meeting_for_reseller(self):
        """ Open meeting's calendar view to schedule meeting on current opportunity.
            :return dict: dictionary value for created Meeting view
        """
        self.ensure_one()
        action = self.env.ref('calendar.action_calendar_event').read()[0]
        partner_ids = self.env.user.partner_id.ids
        if self.partner_id:
            partner_ids.append(self.partner_id.id)
        action['context'] = {
            'default_reseller_op_id': self.id,
            'search_default_reseller_op_id': self.id,
            'default_opportunity_id': self.parent_id.id,
            'default_partner_id': self.partner_id.id,
            'default_partner_ids': partner_ids,
            'default_team_id': self.team_id.id,
            'default_name': self.name,
        }
        return action

    @api.multi
    def action_set_won_rainbowman(self):
        res = super(AceOpportunityReseller, self).action_set_won_rainbowman()
        if not self.env.context.get('run_from_parent', False):
            self.parent_id.action_set_won_rainbowman()
        return {
            'type': 'ir.actions.act_view_reload',
        }

    @api.multi
    def toggle_active(self):
        res = super(AceOpportunityReseller, self).toggle_active()
        if not self.env.context.get('run_from_parent', False):
            self.parent_id.toggle_active()
        return {
            'type': 'ir.actions.act_view_reload',
        }

    @api.multi
    def do_refresh(self):
        return True


