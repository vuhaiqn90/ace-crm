# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from odoo.exceptions import UserError


class TMGCommission(models.TransientModel):
    _name = 'tmg.commission'

    date_from = fields.Date(string='Từ ngày', default=lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date(string='Đến ngày', default=lambda *a: str(datetime.now() +
                                                                   relativedelta(months=+1, day=1, days=-1))[:10])
    user_id = fields.Many2one('res.users', string='Nhân viên kinh doanh')
    category_ids = fields.Many2many('product.category', string='Nhóm sản phẩm tính hoa hồng')
    line_ids = fields.One2many('tmg.commission.line', 'report_id')
    total = fields.Float(compute='get_amount', string='Tổng doanh số')
    total_discount = fields.Float(compute='get_amount', string='Tổng chiết khấu')
    total_returned = fields.Float(compute='get_amount', string='Tổng trả lại')
    total_cost = fields.Float(compute='get_amount', string='Tổng tiền vốn')
    net_revenue = fields.Float(compute='get_amount', string='Tổng doanh thu thuần')
    commission_revenue = fields.Float(compute='get_amount', string='Tổng doanh thu tính hoa hồng')
    gross_profit = fields.Float(compute='get_amount', string='Tổng lợi nhuận gộp')
    commission = fields.Float(compute='get_amount', string='Tổng hoa hồng')

    @api.depends('line_ids')
    def get_amount(self):
        self.update({
            'total': sum(l.total for l in self.line_ids),
            'total_discount': sum(l.total_discount for l in self.line_ids),
            'total_returned': sum(l.total_returned for l in self.line_ids),
            'total_cost': sum(l.total_cost for l in self.line_ids),
            'net_revenue': sum(l.net_revenue for l in self.line_ids),
            'commission_revenue': sum(l.commission_revenue for l in self.line_ids),
            'gross_profit': sum(l.gross_profit for l in self.line_ids),
            'commission': sum(l.commission for l in self.line_ids),
        })

    @api.model
    def default_get(self, fields):
        res = super(TMGCommission, self).default_get(fields)
        category_ids = self.env['product.category'].search([('name', '=', 'Rượu')])
        if category_ids:
            res.update({'category_ids': [(6, 0, category_ids.ids)]})
        return res

    @api.multi
    def compute_commission(self):
        self.line_ids = [(5,)]
        category = ""
        if self.category_ids:
            category_ids = self.env['product.category'].search([('id', 'child_of', self.category_ids.ids)])
            category = len(category_ids) > 1 and """AND pc.id IN {}""".format(tuple(category_ids.ids)) or \
                        """AND pc.id = {}""".format(category_ids.id)
        cr = self._cr
        # cr.execute("""
        #     SELECT ai.id,
        #            ai.number,
        #            ai.date_invoice,
        #            sum(ail.quantity * ail.price_unit) total,
        #            ai.amount_discount,
        #            0 AS refund,
        #            sum(ail.quantity * ail.price_unit) - ai.amount_discount AS net,
        #            sum(ril.price_total) ruou
        #     FROM account_invoice ai
        #         JOIN account_invoice_line ail ON ail.invoice_id = ai.id
        #         LEFT JOIN account_invoice_line ril ON ril.invoice_id = ai.id
        #         LEFT JOIN product_product pp ON pp.id = ril.product_id
        #         LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
        #         LEFT JOIN product_category pc ON pc.id = pt.categ_id %s
        #     WHERE ai.date_invoice BETWEEN %s AND %s
        #       AND ai.state IN ('open', 'in_payment', 'paid')
        #       AND ai.type = 'out_invoice'
        #       AND ai.user_id = %s
        #       AND pc.name IS NOT NULL
        #     GROUP BY ai.id, ai.number, ai.date_invoice, ai.amount_discount
        #     UNION ALL
        #     SELECT ai.id,
        #            ai.number,
        #            ai.date_invoice,
        #            sum(ail.quantity * ail.price_unit) total,
        #            ai.amount_discount,
        #            0 AS refund,
        #            sum(ail.quantity * ail.price_unit) - ai.amount_discount AS net,
        #            sum(ail.price_total) ruou
        #     FROM account_move_line aml
        #         JOIN account_partial_reconcile apr ON apr.credit_move_id = aml.id
        #         JOIN account_move_line dml ON dml.id = apr.debit_move_id
        #         JOIN account_move dm ON dm.id = dml.move_id
        #         JOIN account_invoice ai ON ai.move_id = dm.id
        #         LEFT JOIN account_invoice_line ail ON ail.invoice_id = ai.id
        #         LEFT JOIN product_product pp ON pp.id = ail.product_id
        #         LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
        #         LEFT JOIN product_category pc ON pc.id = pt.categ_id %s
        #     WHERE aml.date BETWEEN %s AND %s
        #       AND (ai.date_invoice < %s OR ai.date_invoice > %s)
        #       AND ai.type = 'out_invoice'
        #       AND ai.user_id = %s
        #       AND pc.name IS NOT NULL
        #     GROUP BY ai.id, ai.number, ai.date_invoice, ai.amount_discount
        #     UNION ALL
        #     SELECT ai.id,
        #            ai.number,
        #            ai.date_invoice,
        #            0 total, -ai.amount_discount,
        #            sum(ail.quantity * ail.price_unit) refund,
        #            0 + ai.amount_discount - sum(ail.quantity * ail.price_unit) net, -sum(ril.price_total) ruou
        #     FROM account_invoice ai
        #         JOIN account_invoice_line ail ON ail.invoice_id = ai.id
        #         LEFT JOIN account_invoice_line ril ON ril.invoice_id = ai.id
        #         LEFT JOIN product_product pp ON pp.id = ril.product_id
        #         LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
        #         LEFT JOIN product_category pc ON pc.id = pt.categ_id %s
        #     WHERE ai.date_invoice BETWEEN %s AND %s
        #       AND ai.state IN ('open', 'in_payment', 'paid')
        #       AND ai.type = 'out_refund'
        #       AND ai.user_id = %s
        #       AND pc.name IS NOT NULL
        #     GROUP BY ai.id, ai.number, ai.date_invoice, ai.amount_discount
        #     ORDER BY date_invoice, id
        # """, (category, self.date_from, self.date_to, self.user_id.id, category, self.date_from, self.date_to,
        #       self.date_from, self.date_to, self.user_id.id, category, self.date_from, self.date_to, self.user_id.id))
        sql = """
            SELECT ai.id,
                   ai.number,
                   ai.date_invoice,
                   ai.amount_untaxed + ai.amount_discount AS total,
                   ai.amount_discount,
                   0 AS refund,
                   ai.amount_untaxed AS net,
                   sum(ril.price_subtotal) ruou,
                   0 AS out_range
            FROM account_invoice ai
                --JOIN account_invoice_line ail ON ail.invoice_id = ai.id
                LEFT JOIN account_invoice_line ril ON ril.invoice_id = ai.id
                LEFT JOIN product_product pp ON pp.id = ril.product_id
                LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                LEFT JOIN product_category pc ON pc.id = pt.categ_id %s
            WHERE ai.date_invoice BETWEEN '%s' AND '%s'
              AND ai.state IN ('open', 'in_payment', 'paid')
              AND ai.type = 'out_invoice'
              AND ai.user_id = %s
              AND pc.name IS NOT NULL
            GROUP BY ai.id, ai.number, ai.date_invoice, ai.amount_discount
            UNION ALL
            SELECT ai.id,
                   ai.number,
                   ai.date_invoice,
                   0 total,
                   ai.amount_discount,
                   0 AS refund,
                   sum(aml.credit) AS net,
                   sum(aml.credit) * sum(COALESCE(ril.price_subtotal, 0)) / COALESCE(ai.amount_untaxed, 1) AS ruou,
                   1 AS out_range
            FROM account_move_line aml
                JOIN account_partial_reconcile apr ON apr.credit_move_id = aml.id
                JOIN account_move_line dml ON dml.id = apr.debit_move_id
                JOIN account_move dm ON dm.id = dml.move_id
                JOIN account_invoice ai ON ai.move_id = dm.id
                LEFT JOIN account_invoice_line ril ON ril.invoice_id = ai.id
                LEFT JOIN product_product pp ON pp.id = ril.product_id
                LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                LEFT JOIN product_category pc ON pc.id = pt.categ_id %s
            WHERE aml.date BETWEEN '%s' AND '%s'
              AND (ai.date_invoice < '%s' OR ai.date_invoice > '%s')
              AND ai.type = 'out_invoice'
              AND ai.user_id = %s
              AND pc.name IS NOT NULL
            GROUP BY ai.id, ai.number, ai.date_invoice, ai.amount_discount, ai.amount_untaxed
            UNION ALL
            SELECT ai.id,
                   ai.number,
                   ai.date_invoice,
                   0 total, -ai.amount_discount,
                   ai.amount_untaxed + ai.amount_discount AS refund,
                   -ai.amount_untaxed AS net, -sum(ril.price_total) ruou,
                   0 AS out_range
            FROM account_invoice ai
                --JOIN account_invoice_line ail ON ail.invoice_id = ai.id
                LEFT JOIN account_invoice_line ril ON ril.invoice_id = ai.id
                LEFT JOIN product_product pp ON pp.id = ril.product_id
                LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                LEFT JOIN product_category pc ON pc.id = pt.categ_id %s
            WHERE ai.date_invoice BETWEEN '%s' AND '%s'
              AND ai.state IN ('open', 'in_payment', 'paid')
              AND ai.type = 'out_refund'
              AND ai.user_id = %s
              AND pc.name IS NOT NULL
            GROUP BY ai.id, ai.number, ai.date_invoice, ai.amount_discount
            ORDER BY date_invoice, id
        """ % (category, self.date_from, self.date_to, self.user_id.id, category, self.date_from, self.date_to,
              self.date_from, self.date_to, self.user_id.id, category, self.date_from, self.date_to, self.user_id.id)
        cr.execute(sql)
        invoices = cr.dictfetchall()
        params = []
        total_net = sum(inv['net'] for inv in invoices) if invoices else 0
        net_revenue_accrued = 0
        # Lấy tỉ lệ chiết khấu
        config_ids = self.env['ace.commission.config'].search([
            ('type', '=', 'sale'),
            ('trial', '=', self.user_id.trial)
        ])
        rate_lst = []
        for cf in config_ids:
            if rate_lst:
                rate_lst[-1][2] = cf.total
            rate_lst += [[cf.rate, cf.total, False, cf.delta_method]]  # [rate, min, max, delta method]
        if not rate_lst:
            raise UserError(_("Vui lòng cấu hình hoa hồng!"))
        # Lấy danh sách cấu hình tỉ lệ hoa hồng theo chiết khấu
        discount_config_ids = self.env['ace.commission.discount.config'].search([
            ('type', '=', 'sale'),
        ])
        discount_config_ids = sorted(discount_config_ids, key=lambda r: (r.sequence, r.id))
        discount_rate_lst = []
        for cf in discount_config_ids:
            if discount_rate_lst:
                discount_rate_lst[-1][2] = cf.discount
            discount_rate_lst += [[cf.rate, cf.discount, False]]  # [rate, min, max]
        if not discount_rate_lst:
            raise UserError(_("Vui lòng cấu hình hoa hồng theo chiết khấu!"))
        query = """
            INSERT INTO tmg_commission_line
                        (create_uid, write_uid, create_date, write_date, report_id, 
                         date, invoice_id, name, total, total_discount, total_returned, net_revenue, commission_revenue, total_cost,
                         gross_profit, gross_profit_per, net_revenue_accrued, discount, commission_revenue_per, 
                         commission_per, receivable, commission, profit_after_sale, profit_after_sale_per)
                         VALUES 
        """
        for inv in invoices:
            query += """(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            if inv != invoices[-1]:
                query += """, """
            invoice_id = self.env['account.invoice'].browse(inv['id'])
            if inv['out_range'] == 1:
                account_move_line_ids = False
            else:
                stock_move_line_ids = invoice_id.mapped(
                    'invoice_line_ids.sale_line_ids.move_ids').filtered(
                    lambda x: x.state == 'done' and (x.location_dest_id.usage == 'customer' or x.location_id == 'customer'))
                account_move_line_ids = self.env['account.move'].search(
                    [('stock_move_id', 'in', stock_move_line_ids and stock_move_line_ids.ids or [])])
            # Tổng doanh số bán rượu và phụ kiện
            total = inv.get('total') or 0
            # Tổng chiết khấu rượu và phụ kiện
            amount_discount = inv.get('amount_discount') if inv['out_range'] != 1 else 0
            # Tổng giá trị trả lại
            returned = inv.get('refund') or 0
            # Tổng giá vốn
            total_cost = sum(m.amount * (1 if m.stock_move_id.location_dest_id.usage == 'customer' else -1)
                             for m in account_move_line_ids) if account_move_line_ids else 0
            # Doanh thu thuần
            net_revenue = inv.get('net') if inv['out_range'] != 1 else 0
            # Doanh thu tính hoa hồng
            commission_revenue = inv.get('ruou') or 0
            # Lợi nhuận gộp
            gross_profit = net_revenue - total_cost
            # % Lọi nhuận gộp
            gross_profit_per = gross_profit / total if total != 0 else 0
            # Doanh thu thuần tích lũy
            net_revenue_accrued += net_revenue
            # % Chiết khấu
            if total != 0:
                discount = amount_discount / total * 100
            elif inv['out_range'] == 1:
                discount = inv.get('amount_discount') / sum(l.quantity * l.price_unit for l in invoice_id.invoice_line_ids) * 100
            else:
                discount = 0
            # % Hoa hồng theo doanh thu
            commission_revenue_per = 0
            if total_net <= rate_lst[0][2]:
                commission_revenue_per = rate_lst[0][0]
            else:
                if net_revenue_accrued <= 0:
                    commission_revenue_per = 0
                else:
                    for rt in rate_lst:
                        if rt == rate_lst[0]:
                            continue
                        if net_revenue_accrued < rt[2]:
                            commission_revenue_per = rt[0]
                            break
                        commission_revenue_per = rate_lst[-1][0]
            # % Hoa hồng được hưởng
            commission_per = 0
            for rt in discount_rate_lst:
                if not discount:
                    commission_per = commission_revenue_per
                    break
                if rt[1] < discount <= rt[2]:
                    if rt == discount_rate_lst[0]:
                        commission_per = commission_revenue_per
                        break
                    else:
                        commission_per = rt[0]
                        break
                if rt == discount_rate_lst[-1] and discount >= rt[1]:
                    commission_per = 0
            # Công nợ còn lại
            credit_move_ids = invoice_id.move_id.line_ids.mapped('matched_credit_ids.credit_move_id').filtered(lambda r: r.date <= self.date_to)
            # receivable = invoice_id.residual if invoice_id.type == 'out_invoice' and inv['out_range'] != 1 else 0
            receivable = invoice_id.amount_total - (sum(l.credit for l in credit_move_ids) if invoice_id.type == 'out_invoice' and inv[
                'out_range'] != 1 and credit_move_ids else 0)
            # Hoa hồng
            if not commission_per:
                commission = 0
            else:
                commission = (commission_revenue - receivable) * commission_per / 100 if commission_revenue > receivable else 0
            # Lợi nhuận sau bán hàng
            profit_after_sale = gross_profit - commission
            # % Lợi nhuận sau bán hàng
            profit_after_sale_per = profit_after_sale / total * 100 if total != 0 else 0
            params += [self._uid, self._uid, datetime.now(), datetime.now(), self.id,
                       inv.get('date_invoice') or '', inv.get('id') or None, inv.get('number') or '', total, amount_discount, returned,
                       net_revenue, commission_revenue, total_cost, gross_profit, gross_profit_per, net_revenue_accrued,
                       discount, commission_revenue_per * (1 if invoice_id.type == 'out_invoice' else -1),
                       commission_per * (1 if invoice_id.type == 'out_invoice' else -1), receivable, commission,
                       profit_after_sale, profit_after_sale_per]
        if params:
            cr.execute(query, params)


class TMGCommissionLine(models.TransientModel):
    _name = 'tmg.commission.line'
    _order = 'date, invoice_id'

    report_id = fields.Many2one('tmg.commission')
    date = fields.Date('Ngày hóa đơn')
    invoice_id = fields.Integer('Hóa đơn')
    name = fields.Char('Hóa đơn')
    total = fields.Float('Tổng doanh số')
    total_discount = fields.Float('Tổng chiết khấu')
    total_returned = fields.Float('Tổng trả lại')
    net_revenue = fields.Float('Tổng doanh thu thuần')
    commission_revenue = fields.Float('Tổng doanh thu tính hoa hồng')
    total_cost = fields.Float('Tổng tiền vốn')
    gross_profit = fields.Float('Lợi nhuận gộp')
    gross_profit_per = fields.Float('Phần trăm lợi nhuận gộp')
    net_revenue_accrued = fields.Float('Doanh thu thuần tích lũy')
    discount = fields.Float('% Chiết khấu')
    commission_revenue_per = fields.Float('% Hoa hồng theo doanh thu')
    commission_per = fields.Float('% Hoa hồng được hưởng')
    receivable = fields.Float('Công nợ')
    commission = fields.Float('Hoa hồng')
    profit_after_sale = fields.Float('Lợi nhuận sau bán hàng')
    profit_after_sale_per = fields.Float('% Lợi nhuận sau bán hàng')


