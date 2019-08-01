# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, timedelta

class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    license_code = fields.Char("License Code")

    @api.model
    def start_create_opportunity(self, days=30):
        line_ids = self.search([
            ('date', '=', datetime.now().date() + timedelta(days=days)),
            ('template_id.recurring_rule_boundary', '=', 'limited'),
        ]).mapped('recurring_invoice_line_ids')
        data = {}
        for line in line_ids:
            customer_id = line.analytic_account_id.partner_id
            vals = {
                'category_id': line.product_id.categ_id.id,
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'product_tmpl_id': line.product_id.product_tmpl_id.id,
                'product_qty': 1,
                'product_uom': line.product_id.uom_id.id,
                'price_unit': line.price_unit,
                'company_id': line.analytic_account_id.company_id.id
            }
            if customer_id not in data:
                data[customer_id] = {
                    'partner_id': customer_id.id,
                    'name': 'Renew services - %s' % customer_id.name,
                    'type': 'opportunity',
                    'email_from': customer_id.email or '',
                    'phone': customer_id.phone or '',
                    'lead_line_ids': [(0, 0, vals)],
                    'user_id': False,
                    'team_id': False,
                    'company_id': customer_id.company_id.id
                }
            else:
                data[customer_id]['lead_line_ids'].append((0, 0, vals))
        for index, oppor in enumerate(data):
            self.env['crm.lead'].with_context(force_company=data[oppor].get('company_id')).sudo().create(data[oppor])