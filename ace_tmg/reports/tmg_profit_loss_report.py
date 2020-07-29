# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from odoo.exceptions import UserError


class TMGProfitLossReport(models.TransientModel):
    _name = 'tmg.profit.loss.report'

    date_from = fields.Date(string='Từ ngày', default=lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date(string='Đến ngày', default=lambda *a: str(datetime.now() +
                                                                    relativedelta(months=+1, day=1, days=-1))[:10])
    user_id = fields.Many2one('res.users', string='Nhân viên kinh doanh')
    partner_ids = fields.Many2many('res.partner', string='Khách hàng')
    product_ids = fields.Many2many('product.product', string='Sản phẩm')
    category_ids = fields.Many2many('product.category', string='Nhóm Sản phẩm')
    type = fields.Selection([('customer', 'Khách hàng'), ('product', 'Sản phẩm')],
                            default='customer', string='Xem theo')
    total_selling_expense = fields.Float(string='Tổng chi phí bán hàng')
    total_management_cost = fields.Float(string='Tổng chi phí quản lý')
    line_ids = fields.One2many('tmg.profit.loss.line', 'report_id')
    group_line_ids = fields.One2many('tmg.profit.loss.group.product', 'report_id')

    @api.multi
    def get_report(self):
        self.line_ids = [(5,)]
        self.group_line_ids = [(5,)]
        cr = self._cr
        if self.type == 'customer':
            user = partner = ''
            if self.user_id:
                user = """AND ai.user_id = {}""".format(self.user_id.id)
            if self.partner_ids:
                partner = len(self.partner_ids) > 1 and """AND ai.partner_id IN {}""".format(tuple(self.partner_ids.ids)) \
                          or """AND ai.partner_id = {}""".format(self.partner_ids.id)
            sql = """
                SELECT ai.partner_id,
                       SUM(ail.quantity) AS qty,
                       SUM(ai.amount_untaxed + ai.amount_discount) AS total,
                       SUM(ai.amount_discount) AS discount
                FROM account_invoice ai
                    JOIN account_invoice_line ail ON ail.invoice_id = ai.id
                WHERE ai.date_invoice BETWEEN '%s' AND '%s'
                  AND ai.state IN ('open', 'in_payment', 'paid')
                  AND ai.type = 'out_invoice' %s %s
                GROUP BY ai.partner_id
            """ % (self.date_from, self.date_to, user, partner)
            cr.execute(sql)
            res = cr.dictfetchall()
            query = """
                INSERT INTO tmg_profit_loss_line
                            (create_uid, write_uid, create_date, write_date, report_id, 
                             partner_id, qty, turnover, discount, refund, discount_rate, net_revenue, cost, 
                             gross_profit, gross_profit_rate, net_revenue_rate, selling_expense, selling_expense_rate, 
                             management_cost, management_cost_rate, profit_untaxed, profit_rate)
                             VALUES 
            """
            data = []
            for line in res:
                qty = line['qty']
                turnover = line['total']
                discount = line['discount']
                refund_sql = """
                    SELECT ai.partner_id,
                           SUM(ai.amount_untaxed) AS net
                    FROM account_invoice ai
                    WHERE ai.date_invoice BETWEEN '%s' AND '%s'
                      AND ai.state IN ('open', 'in_payment', 'paid')
                      AND ai.type = 'out_refund'
                      AND ai.partner_id = %s %s
                    GROUP BY ai.partner_id
                """ % (self.date_from, self.date_to, line['partner_id'], user)
                cr.execute(refund_sql)
                refund = cr.dictfetchone()
                refund = refund['net'] if refund else 0
                discount_rate = discount / turnover if turnover != 0 else 0
                net_revenue = turnover - discount - refund
                cost_sql = """
                    SELECT SUM(aml.balance) AS total
                    FROM account_move_line aml
                        JOIN account_journal aj ON aj.id = aml.journal_id
                        JOIN account_account aa ON aa.id = aml.account_id
                        JOIN account_move am ON am.id = aml.move_id
                        JOIN stock_move sm ON sm.id = am.stock_move_id
                        JOIN sale_order_line sol ON sol.id = sm.sale_line_id
                        JOIN sale_order so ON so.id = sol.order_id
                    WHERE aj.code = 'STJ' 
                        AND aa.code LIKE '%s' 
                        AND aml.partner_id = %s 
                        %s
                        AND aml.date BETWEEN '%s' AND '%s'
                """ % ('632%', line['partner_id'], self.user_id and """AND so.user_id = {}""".format(self.user_id.id) or "", self.date_from, self.date_to)
                cr.execute(cost_sql)
                cost = cr.fetchone()
                cost = cost and cost[0] or 0
                gross_profit = net_revenue - cost
                gross_profit_rate = gross_profit / turnover if turnover != 0 else 0
                data.append({
                    'partner_id': line['partner_id'],
                    'qty': qty,
                    'turnover': turnover,
                    'discount': discount,
                    'refund': refund,
                    'discount_rate': discount_rate,
                    'net_revenue': net_revenue,
                    'cost': cost,
                    'gross_profit': gross_profit,
                    'gross_profit_rate': gross_profit_rate,
                })
            total_net_revenue = sum(item['net_revenue'] for item in data)
            params = []
            for item in data:
                query += """(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                if item != data[-1]:
                    query += """, """
                net_revenue_rate = item['net_revenue'] / total_net_revenue if total_net_revenue != 0 else 0
                selling_expense = net_revenue_rate * self.total_selling_expense
                selling_expense_rate = selling_expense / item['net_revenue'] if item['net_revenue'] != 0 else 0
                management_cost = net_revenue_rate * self.total_management_cost
                management_cost_rate = management_cost / item['net_revenue'] if item['net_revenue'] != 0 else 0
                profit_untaxed = item['net_revenue'] - selling_expense - management_cost
                profit_rate = profit_untaxed / item['turnover'] if item['turnover'] != 0 else 0
                params += [self._uid, self._uid, datetime.now(), datetime.now(), self.id,
                           item['partner_id'], item['qty'], item['turnover'], item['discount'], item['refund'],
                           item['discount_rate'] * 100, item['net_revenue'], item['cost'], item['gross_profit'],
                           item['gross_profit_rate'] * 100, net_revenue_rate * 100, selling_expense, selling_expense_rate * 100,
                           management_cost, management_cost_rate * 100, profit_untaxed, profit_rate * 100]
            if params:
                cr.execute(query, params)
        else:
            product = category = ''
            if self.product_ids:
                product = len(self.product_ids) > 1 and """AND ail.product_id IN {}""".format(tuple(self.product_ids.ids)) \
                          or """AND ail.product_id = {}""".format(self.product_ids.id)
            if self.category_ids:
                category_ids = self.env['product.category'].search([('id', 'child_of', self.category_ids.ids)])
                category = len(category_ids) > 1 and """AND pt.categ_id IN {}""".format(tuple(category_ids.ids)) \
                          or """AND pt.categ_id = {}""".format(category_ids.id)
            # Lấy doanh số, chiết khấu theo sản phẩm
            sql = """
                SELECT ail.product_id, pt.categ_id, 
                       SUM(ail.quantity) AS qty,
                       SUM(ail.quantity * ail.price_unit) AS total,
                       SUM(ail.quantity * ail.price_unit * COALESCE(ail.discount, 0) / 100 + COALESCE(ail.discount_amount, 0)) AS discount
                FROM account_invoice ai
                    JOIN account_invoice_line ail ON ail.invoice_id = ai.id
                    JOIN product_product pp ON pp.id = ail.product_id
                    JOIN product_template pt ON pt.id = pp.product_tmpl_id
                WHERE ai.date_invoice BETWEEN '%s' AND '%s'
                  AND ai.state IN ('open', 'in_payment', 'paid')
                  AND ai.type = 'out_invoice' %s %s
                GROUP BY ail.product_id, pt.categ_id
            """ % (self.date_from, self.date_to, product, category)
            cr.execute(sql)
            res = cr.dictfetchall()
            # Danh sách báo cáo lãi lỗ theo sản phẩm
            query = """
                INSERT INTO tmg_profit_loss_line
                            (create_uid, write_uid, create_date, write_date, report_id, 
                             product_id, qty, turnover, discount, refund, discount_rate, net_revenue, cost, cost_rate,
                             gross_profit, gross_profit_rate, net_revenue_rate, selling_expense, selling_expense_rate, 
                             management_cost, management_cost_rate, profit_untaxed, profit_rate)
                             VALUES 
            """
            # Danh sách báo cáo lãi lỗ theo nhóm sản phẩm
            group_query = """
                INSERT INTO tmg_profit_loss_group_product
                            (create_uid, write_uid, create_date, write_date, report_id, 
                             category_id, turnover, turnover_rate, net_revenue, net_revenue_rate, cost, cost_rate)
                             VALUES 
            """
            data = []
            # Lấy thông tin theo sản phẩm
            for line in res:
                product_id = self.env['product.product'].browse(line['product_id'])
                # Số lượng
                qty = line['qty']
                # Doanh số
                turnover = line['total']
                # Chiết khấu
                discount = line['discount']
                # Lấy tổng doanh thu trả lại theo sản phẩm
                refund_sql = """
                    SELECT ail.product_id,
                           SUM(ail.quantity * ail.price_unit - (ail.quantity * ail.price_unit * COALESCE(ail.discount, 0) / 100 + COALESCE(ail.discount_amount, 0))) AS net
                    FROM account_invoice ai
                        JOIN account_invoice_line ail ON ail.invoice_id = ai.id
                    WHERE ai.date_invoice BETWEEN '%s' AND '%s'
                      AND ai.state IN ('open', 'in_payment', 'paid')
                      AND ai.type = 'out_refund'
                      AND ail.product_id = %s
                    GROUP BY ail.product_id
                """ % (self.date_from, self.date_to, line['product_id'])
                cr.execute(refund_sql)
                refund = cr.dictfetchone()
                # Trả lại
                refund = refund['net'] if refund else 0
                # Tỷ lệ chiết khấu
                discount_rate = discount / turnover if turnover != 0 else 0
                # Doanh thu
                net_revenue = turnover - discount - refund
                # Lấy bút toán giá vốn theo sản phẩm
                cost_sql = """
                    SELECT SUM(aml.balance) AS total
                    FROM account_move_line aml
                        JOIN account_journal aj ON aj.id = aml.journal_id
                        JOIN account_account aa ON aa.id = aml.account_id
                    WHERE aj.code = 'STJ' AND aa.code LIKE '%s' AND aml.product_id = %s AND aml.date BETWEEN '%s' AND '%s'
                """ % ('632%', line['product_id'], self.date_from, self.date_to)
                cr.execute(cost_sql)
                cost = cr.fetchone()
                # Giá vốn
                cost = cost and cost[0] or 0
                # Tỷ lệ GV/DS
                cost_rate = cost / turnover if turnover != 0 else 0
                # Lợi nhuận gộp
                gross_profit = net_revenue - cost
                # Tỷ lệ LN gộp / DS
                gross_profit_rate = gross_profit / turnover if turnover != 0 else 0
                data.append({
                    'product_id': line['product_id'],
                    'category_id': product_id.categ_id.id,
                    'qty': qty,
                    'turnover': turnover,
                    'discount': discount,
                    'refund': refund,
                    'discount_rate': discount_rate,
                    'net_revenue': net_revenue,
                    'cost': cost,
                    'cost_rate': cost_rate,
                    'gross_profit': gross_profit,
                    'gross_profit_rate': gross_profit_rate,
                })
            # Tổng doanh thu theo sản phẩm
            total_turnover = sum(item['turnover'] for item in data)
            total_net_revenue = sum(item['net_revenue'] for item in data)
            params = []
            group_params = []
            group_data = {}
            # Lấy thông tin còn lại sau khi có tổng doanh thu
            for item in data:
                query += """(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                if item != data[-1]:
                    query += """, """
                # Tỷ lệ doanh thu / tổng doanh thu
                net_revenue_rate = item['net_revenue'] / total_net_revenue if total_net_revenue != 0 else 0
                # Chi phí bán hàng
                selling_expense = net_revenue_rate * self.total_selling_expense
                # Tỷ lệ chi phí bán hàng / doanh thu
                selling_expense_rate = selling_expense / item['net_revenue'] if item['net_revenue'] != 0 else 0
                # Chi phí quản lý
                management_cost = net_revenue_rate * self.total_management_cost
                # Tỷ lệ chi phí quản lý / doanh thu
                management_cost_rate = management_cost / item['net_revenue'] if item['net_revenue'] != 0 else 0
                # Lợi nhuận trước thuế
                profit_untaxed = item['net_revenue'] - selling_expense - management_cost
                # Tỷ lệ LN / DS
                profit_rate = profit_untaxed / item['turnover'] if item['turnover'] != 0 else 0
                params += [self._uid, self._uid, datetime.now(), datetime.now(), self.id,
                           item['product_id'], item['qty'], item['turnover'], item['discount'], item['refund'],
                           item['discount_rate'] * 100, item['net_revenue'], item['cost'], item['cost_rate'] * 100,
                           item['gross_profit'], item['gross_profit_rate'] * 100, net_revenue_rate * 100, selling_expense,
                           selling_expense_rate * 100, management_cost, management_cost_rate * 100, profit_untaxed, profit_rate * 100]
                # Group thông tin theo nhóm sản phẩm
                if item['category_id'] not in group_data:
                    group_data[item['category_id']] = [item['turnover'], item['net_revenue'], item['cost']]
                else:
                    group_data[item['category_id']][0] += item['turnover']
                    group_data[item['category_id']][1] += item['net_revenue']
                    group_data[item['category_id']][2] += item['cost']
            for key, value in group_data.items():
                group_query += """(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                if key != list(group_data)[-1]:
                    group_query += """, """
                # Doanh số
                g_turnover = value[0]
                # Tỷ lệ DS / Tổng DS
                g_turnover_rate = g_turnover / total_turnover
                # Doanh thu
                g_net_revenue = value[1]
                # Tỷ lệ DT / Tổng DT
                g_net_revenue_rate = g_net_revenue / total_net_revenue
                # Giá vốn
                g_cost = value[2]
                # Tỷ lệ GV/DS
                g_cost_rate = g_cost / g_turnover
                group_params += [self._uid, self._uid, datetime.now(), datetime.now(), self.id,
                                 key, g_turnover, g_turnover_rate * 100, g_net_revenue, g_net_revenue_rate * 100,
                                 g_cost, g_cost_rate * 100]
            if params:
                cr.execute(query, params)
            if group_params:
                cr.execute(group_query, group_params)


class TMGProfitLossLine(models.TransientModel):
    _name = 'tmg.profit.loss.line'

    report_id = fields.Many2one('tmg.profit.loss.report')
    partner_id = fields.Many2one('res.partner', string='Khách hàng')
    product_id = fields.Many2one('product.product', string='Sản phẩm')
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id', string='ĐVT')
    qty = fields.Float('Số lượng')
    turnover = fields.Float('Doanh số')
    discount = fields.Float('Chiết khấu')
    refund = fields.Float('Trả hàng')
    discount_rate = fields.Float('Tỷ lệ CK/DS')
    net_revenue = fields.Float('Doanh thu')
    cost = fields.Float('Giá vốn')
    cost_rate = fields.Float('Tỷ lệ Giá vốn/DS')
    gross_profit = fields.Float('Lợi nhuận gộp')
    gross_profit_rate = fields.Float("Tỷ lệ LN gộp/DS")
    net_revenue_rate = fields.Float('Tỷ lệ DT')
    selling_expense = fields.Float('Chi phí bán hàng')
    selling_expense_rate = fields.Float('Tỷ lệ % CPBH/DT')
    management_cost = fields.Float('Chi phí quản lý')
    management_cost_rate = fields.Float('Tỷ lệ % CPQL/DT')
    profit_untaxed = fields.Float('Lợi nhuận trước thuế')
    profit_rate = fields.Float('Tỷ lệ LN/DS')


class TMGProfitLossGroupProduct(models.TransientModel):
    _name = 'tmg.profit.loss.group.product'

    report_id = fields.Many2one('tmg.profit.loss.report')
    category_id = fields.Many2one('product.category', string='Nhóm sản phẩm')
    turnover = fields.Float('Doanh số')
    turnover_rate = fields.Float('Tỷ lệ % DS/Tổng DS')
    net_revenue = fields.Float('Doanh thu')
    net_revenue_rate = fields.Float('Tỷ lệ % DT/Tổng DT')
    cost = fields.Float('Tiền vốn')
    cost_rate = fields.Float('Tỷ lệ GV/DS')
