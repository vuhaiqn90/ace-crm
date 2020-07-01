# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class ACEWineTryReport(models.TransientModel):
    _name = 'ace.wine.try.report'
    _description = 'Báo cáo rượu thử'

    name = fields.Char(default='Báo cáo rượu thử')
    date_from = fields.Date(string='Từ ngày', default=lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date(string='Đến ngày', default=lambda *a: str(datetime.now() +
                                                                   relativedelta(months=+1, day=1, days=-1))[:10])
    user_ids = fields.Many2many('res.users', string='Nhân viên KD')
    team_ids = fields.Many2many('crm.team', string='Nhóm KD')
    partner_id = fields.Many2one('res.partner', string='Khách hàng')
    total_revenue = fields.Float('Tổng doanh thu')
    rate = fields.Float('% Rượu thử / Doanh thu', compute='get_amount')
    over_amount = fields.Float('Số tiền vượt định mức', compute='get_amount')
    fine = fields.Float('Số tiền NV phải nộp', compute='get_amount')
    line_ids = fields.One2many('ace.wine.try.line', 'report_id')
    emp_line_ids = fields.One2many('ace.wine.try.employee.line', 'report_id')

    @api.depends('line_ids', 'emp_line_ids')
    def get_amount(self):
        for record in self:
            record.rate = sum(l.rate for l in record.emp_line_ids)
            record.over_amount = sum(l.over_amount for l in record.emp_line_ids)
            record.fine = sum(l.fine for l in record.emp_line_ids)

    def get_report(self):
        self.line_ids = [(5,)]
        self.emp_line_ids = [(5,)]
        cr = self._cr
        self.total_revenue = self.rate = self.over_amount = self.fine = 0
        partner = users = teams = ''
        if self.partner_id:
            partner += """AND so.partner_id = {}""".format(self.partner_id.id)
        if self.user_ids:
            users += len(self.user_ids) == 1 and """AND so.user_id = {}""".format(self.user_ids.id) \
                     or """AND so.user_id IN {}""".format(tuple(self.user_ids.ids))
        if self.team_ids:
            teams += len(self.team_ids) == 1 and """AND so.team_id = {}""".format(self.team_ids.id) \
                     or """AND so.team_id IN {}""".format(tuple(self.team_ids.ids))
        sql = """
            SELECT sol.id, sol.order_id, so.partner_id, so.user_id, sol.product_id, sol.product_uom AS uom, 
                   sol.product_uom_qty AS qty, sol.price_unit AS price, sol.product_uom_qty * sol.price_unit AS amount
            FROM sale_order_line sol 
                JOIN sale_order so ON so.id = sol.order_id
                JOIN account_analytic_tag_sale_order_line_rel rel ON rel.sale_order_line_id = sol.id
                JOIN account_analytic_tag aat ON aat.id = rel.account_analytic_tag_id AND aat.name = 'Rượu thử'
            WHERE so.user_id IS NOT NULL AND so.date_order >= '%s' AND so.date_order <= '%s' %s %s %s
        """ % (self.date_from.strftime('%Y-%m-%d 00:00:00'), self.date_to.strftime('%Y-%m-%d 23:59:59'),
               partner, users, teams)
        cr.execute(sql)
        res = cr.dictfetchall()
        params = []
        ids = []
        # Tong so luong ruou thu theo NVKD
        list_qty = {}
        # Tong tien ruou thu theo NVKD
        list_amount = {}
        # Lay thong tin chi tiet ruou thu
        query = """
            INSERT INTO ace_wine_try_line
                        (create_uid, write_uid, create_date, write_date, report_id, order_id, partner_id, 
                         user_id, product_id, uom_id, qty, price_unit, amount)
                         VALUES 
        """
        for item in res:
            if item.get('user_id') not in list_qty:
                list_qty[item.get('user_id')] = item.get('qty') or 0
            else:
                list_qty[item.get('user_id')] += (item.get('qty') or 0)
            if item.get('user_id') not in list_amount:
                list_amount[item.get('user_id')] = item.get('amount') or 0
            else:
                list_amount[item.get('user_id')] += (item.get('amount') or 0)
            ids += [item.get('id')]
            query += """(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            if item != res[-1]:
                query += """, """
            params += [self._uid, self._uid, datetime.now(), datetime.now(), self.id, item.get('order_id') or None,
                       item.get('partner_id') or None, item.get('user_id') or None, item.get('product_id') or None,
                       item.get('uom') or None, item.get('qty') or 0, item.get('price') or 0, item.get('amount') or 0]
        if params:
            cr.execute(query, params)
        exception = ids and (len(ids) > 1 and """AND sol.id NOT IN {}""".format(tuple(ids))
                             or """AND sol.id != {}""".format(ids[0])) or ''
        sql = """
            SELECT SUM(sol.price_subtotal) total
            FROM sale_order_line sol 
                JOIN sale_order so ON so.id = sol.order_id
            WHERE so.user_id IS NOT NULL AND so.date_order >= '%s' AND so.date_order <= '%s' %s %s %s %s 
        """ % (self.date_from.strftime('%Y-%m-%d 00:00:00'), self.date_to.strftime('%Y-%m-%d 23:59:59'),
               exception, partner, users, teams)
        cr.execute(sql)
        self.total_revenue = cr.fetchone()[0]
        sql = """
            SELECT so.user_id, SUM(sol.price_subtotal) total
            FROM sale_order_line sol 
                JOIN sale_order so ON so.id = sol.order_id
            WHERE so.user_id IS NOT NULL AND so.date_order >= '%s' AND so.date_order <= '%s' %s %s %s %s 
            GROUP BY so.user_id
        """ % (self.date_from.strftime('%Y-%m-%d 00:00:00'), self.date_to.strftime('%Y-%m-%d 23:59:59'),
               exception, partner, users, teams)
        cr.execute(sql)
        res = cr.dictfetchall()
        params1 = []
        # Lay chi tiet bao cao theo NVKD
        query = """
            INSERT INTO ace_wine_try_employee_line
                        (create_uid, write_uid, create_date, write_date, report_id,
                         user_id, qty, amount, total, rate, over_amount, fine)
                         VALUES 
        """
        for item in res:
            qty = sum(value for key, value in list_qty.items() if key == item.get('user_id'))
            amount = sum(value for key, value in list_amount.items() if key == item.get('user_id'))
            total = item.get('total') or 0
            rate = 0 if total == 0 else total * 0.1
            query += """(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            if item != res[-1]:
                query += """, """
            params1 += [self._uid, self._uid, datetime.now(), datetime.now(), self.id, item.get('user_id') or None,
                        qty or 0, amount or 0, total, rate, amount - rate if amount > rate else 0,
                        amount - rate > 0 and (amount - rate) * 0.5 or 0]
        if params1:
            cr.execute(query, params1)

    @api.multi
    def export_excel(self):
        if not self.user_ids:
            raise UserError(_("Vui lòng chọn Nhân viên KD để in báo cáo!"))
        datas = {'ids': self and self.ids or []}
        datas['model'] = 'ace.wine.try.report'
        datas['form'] = self.sudo().read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        return self.env.ref('ace_tmg.tmg_ruou_thu_py3o').with_context(
            current_date=[datetime.now().day, datetime.now().month, datetime.now().year],
            amount=sum(l.amount for l in self.line_ids)).report_action(self)


class ACEWineTryLine(models.TransientModel):
    _name = 'ace.wine.try.line'
    _description = 'Báo cáo chi tiết rượu thử'
    _order = 'user_id, product_id'

    report_id = fields.Many2one('ace.wine.try.report')
    order_id = fields.Many2one('sale.order', string='Đơn hàng')
    product_id = fields.Many2one('product.product', string='Sản phẩm')
    product_code = fields.Char(string='Mã SP', related='product_id.default_code')
    product_name = fields.Char(string='Tên SP', related='product_id.name')
    partner_id = fields.Many2one('res.partner', string='Khách hàng')
    user_id = fields.Many2one('res.users', string='NVKD')
    uom_id = fields.Many2one('uom.uom', string='ĐVT')
    qty = fields.Float(string='SL rượu thử')
    price_unit = fields.Float(string='Đơn giá')
    amount = fields.Float(string='Tổng tiền rượu thử')


class ACEWineTryEmployeeLine(models.TransientModel):
    _name = 'ace.wine.try.employee.line'
    _description = 'Báo cáo chi tiết rượu thử theo nhân viên'
    _order = 'user_id'

    report_id = fields.Many2one('ace.wine.try.report')
    user_id = fields.Many2one('res.users', string='NVKD')
    uom_id = fields.Many2one('uom.uom', string='ĐVT')
    qty = fields.Float(string='SL rượu thử')
    amount = fields.Float(string='Tổng tiền rượu thử')
    total = fields.Float(string='Tổng doanh thu')
    rate = fields.Float(string='% Rượu thử / Doanh thu')
    over_amount = fields.Float(string='Số tiền vượt định mức')
    fine = fields.Float(string='Số tiền NV phải nộp')