# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
from lxml import etree
from odoo.osv.orm import setup_modifiers


class SaleOrder(models.Model):
    _inherit = "sale.order"

    telesales = fields.Many2one('res.users')

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({'telesales': self.telesales and self.telesales.id or False})
        return invoice_vals

    # @api.multi
    # def check_limit(self):
    #     self.ensure_one()
    #     if self.user_has_groups('sales_team.group_sale_manager'):
    #         return True
    #     partner = self.partner_id
    #     user_id = self.env['res.users'].search([
    #         ('partner_id', '=', partner.id)], limit=1)
    #     if user_id and not user_id.has_group('base.group_portal') or not \
    #             user_id:
    #         moveline_obj = self.env['account.move.line']
    #         movelines = moveline_obj.search([
    #             ('partner_id', '=', partner.id),
    #             ('account_id.user_type_id.name', 'in', ['Receivable', 'Payable']),
    #             ('move_id.state', '=', 'posted'),
    #         ])
    #         credit = sum(line.credit for line in movelines)
    #         debit = sum(line.debit for line in movelines)
    #         available_credit_limit = partner.credit_limit - debit + credit
    #         if self.amount_total > available_credit_limit:
    #             msg = 'Your available credit limit' \
    #                   ' Amount = %s \nCheck "%s" Accounts or Credit ' \
    #                   'Limits.' % (available_credit_limit,
    #                                self.partner_id.name)
    #             raise UserError(_('You can not confirm Sale Order. \n' + msg))
    #         return True

    @api.multi
    def action_cancel(self):
        if any(order.invoice_ids.filtered(lambda i: i.state != 'cancel') for order in self):
            raise UserError(_("Pls cancel invoice first."))
        return super(SaleOrder, self).action_cancel()

    @api.multi
    def unlink(self):
        if any(order.picking_ids or order.invoice_ids for order in self):
            raise UserError(_("Unable to delete sale order as some deliveries or invoices have related."))
        return super(SaleOrder, self).unlink()

    @api.onchange('user_id')
    def change_user_and_get_sales_teams(self):
        self.team_id = False
        if self.user_id:
            team_id = self.env['crm.team']._get_default_team_id(self.user_id.id)
            if team_id:
                self.team_id = team_id.id

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        # if view_type == 'form' and self.user_has_groups('!sales_team.group_sale_manager,!base.group_system'):
        #     res['fields']['order_line']['views']['tree']['fields']['discount']['readonly'] = True
            # res['fields']['partner_id']['invisible'] = True
        # if view_type == 'form' and self.user_has_groups('!sales_team.group_sale_manager,!base.group_system'):
        #     doc = etree.XML(res['arch'])
        #     for node in doc.xpath("//field[@name='partner_id']"):
        #         node.set('readonly', '1')
        #         setup_modifiers(node)
        #     res['arch'] = etree.tostring(doc, encoding='unicode')
        if view_type == 'form' and self.user_has_groups('!sales_team.group_sale_manager,!base.group_system'):
            doc = etree.XML(res['fields']['order_line']['views']['tree']['arch'])
            for node in doc.xpath("//field[@name='discount']"):
                node.set('readonly', '1')
                setup_modifiers(node)
            res['fields']['order_line']['views']['tree']['arch'] = etree.tostring(doc)
        return res