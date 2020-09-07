# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
from lxml import etree
from odoo.osv.orm import setup_modifiers
from dateutil.relativedelta import relativedelta


class SaleOrder(models.Model):
    _inherit = "sale.order"

    telesales = fields.Many2one('res.users')

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({'telesales': self.telesales and self.telesales.id or False})
        return invoice_vals

    @api.multi
    def check_limit(self):
        super(SaleOrder, self).check_limit()
        partner = self.partner_id
        user_id = self.env['res.users'].search([
            ('partner_id', '=', partner.id)], limit=1)
        if partner.alcohol_norms > 0 and user_id:
            cr = self._cr
            date_from = self.date_order.replace(day=1).strftime('%Y-%m-%d 00:00:00')
            date_to = (self.date_order + relativedelta(months=+1, day=1, days=-1)).strftime('%Y-%m-%d 23:59:59')
            order_ids = self.search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['sale', 'done']),
                ('date_order', '>=', date_from),
                ('date_order', '<=', date_to),
            ])
            orders = order_ids and (len(order_ids) > 1 and "AND so.id IN {}".format(tuple(order_ids.ids)) or
                     "AND so.id = {}".format(order_ids[0].id)) or ''
            total = 0
            if orders:
                sql = """
                    SELECT so.partner_id, COALESCE(SUM(sol.price_total), 0) AS total
                    FROM sale_order_line sol 
                        JOIN sale_order so ON so.id = sol.order_id
                        JOIN account_analytic_tag_sale_order_line_rel rel ON rel.sale_order_line_id = sol.id
                        JOIN account_analytic_tag aat ON aat.id = rel.account_analytic_tag_id AND aat.name = 'Rượu thử'
                    WHERE 1=1 %s
                    GROUP BY so.partner_id
                """ % (orders,)
                cr.execute(sql)
                total = cr.dictfetchone()
                if total:
                    total = total['total']
            available_limit = partner.alcohol_norms - total
            if total > partner.alcohol_norms:
                msg = 'Your available alcohol norms' \
                      ' Amount = %s \nCheck "%s" Alcohol Norms.' % (available_limit,
                                   self.partner_id.name)
                raise UserError(_('You can not confirm Sale Order. \n' + msg))
            return True

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
                node.set('force_save', '1')
                setup_modifiers(node)
            res['fields']['order_line']['views']['tree']['arch'] = etree.tostring(doc)
        return res