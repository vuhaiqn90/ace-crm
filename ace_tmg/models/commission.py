# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta


class ACECommission(models.Model):
    _name = "ace.commission"

    name = fields.Char()
    date_from = fields.Date('From', default=lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date('To', default=lambda *a: str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10])
    trial = fields.Boolean('Trial Work')
    job_position = fields.Selection([('sale', 'Salesperson'), ('tels', 'Telesales'), ('ctv', 'CTV')],
                                    string='Job Position')
    user_ids = fields.Many2many('res.users', string='Salesperson/Telesales')
    line_ids = fields.One2many('ace.commission.line', 'commission_id')

    @api.multi
    def compute_commission(self):
        self.line_ids = [(5,)]
        job = self.job_position == 'tels' and """AND ai.telesales IS NOT NULL""" or \
              (self.job_position == 'ctv' and """AND rsp.job_position = 'ctv'""" or """AND COALESCE(rsp.job_position, 'sale') = 'sale'""")
        trial = """AND (rsp.trial = TRUE OR pls.trial = TRUE)"""
        user = self.user_ids and len(self.user_ids) == 1 and \
                """AND (ai.user_id = %s OR ai.telesales = %s)""" % (self.user_ids.id, self.user_ids.id) or \
               (len(self.user_ids) > 1 and """AND (ai.user_id IN %s OR ai.telesales IN %s)""" %
                (tuple(self.user_ids.ids), tuple(self.user_ids.ids)) or """""")
        sql = """
            SELECT ai.id, ai.number, ai.date_invoice, ai.user_id, COALESCE(rsp.job_position, 'sale') AS job_position,
                   ai.amount_untaxed * (CASE WHEN ai.type = 'out_invoice' THEN 1 ELSE -1 END) AS amount_untaxed, 
                   ai.amount_total * (CASE WHEN ai.type = 'out_invoice' THEN 1 ELSE -1 END) AS amount_total,
                   rsp.trial AS sale_trial, ai.telesales, pls.trial AS tels_trial
            FROM account_invoice ai
                LEFT JOIN res_users sp ON sp.id = ai.user_id
                LEFT JOIN res_partner rsp ON rsp.id = sp.partner_id
                LEFT JOIN res_users tls ON tls.id = ai.telesales
                LEFT JOIN res_partner pls ON pls.id = tls.partner_id
            WHERE ai.state IN ('open', 'in_payment', 'paid')
                  AND ai.type IN ('out_invoice', 'out_refund')
                  AND ai.date_invoice BETWEEN '%s' AND '%s'
                  %s %s %s
        """ % (self.date_from, self.date_to, """""" if not self.job_position else job, self.trial and trial or """""", user)
        self._cr.execute(sql)
        invoices = self._cr.dictfetchall()
        data = {}
        for inv in invoices:
            if inv['user_id']:
                if inv['user_id'] not in data:
                    data[inv['user_id']] = {'sale': inv['amount_untaxed']}
                elif 'sale' not in data[inv['user_id']]:
                    data[inv['user_id']]['sale'] = inv['amount_untaxed']
                else:
                    data[inv['user_id']]['sale'] += inv['amount_untaxed']
            if inv['telesales']:
                if inv['telesales'] not in data:
                    data[inv['telesales']] = {'tels': inv['amount_untaxed']}
                elif 'tels' not in data[inv['telesales']]:
                    data[inv['telesales']]['tels'] = inv['amount_untaxed']
                else:
                    data[inv['telesales']]['tels'] += inv['amount_untaxed']
        if data:
            sql_child = ("""INSERT INTO ace_commission_line
                                    (create_uid, write_uid, create_date, write_date,
                                     commission_id, user_id, job_position, trial, 
                                     total, amount, rate, commission)
                            VALUES """)
            params_child = []
            flag = False
            for item in data:
                for item1 in data[item]:
                    user_id = self.env['res.users'].browse(item)
                    type = 'tels' if item1 == 'tels' else user_id.job_position or 'sale'
                    total = data[item][item1]
                    if self.job_position and self.job_position != type:
                        continue
                    if self.trial and not user_id.trial:
                        continue
                    if self.user_ids and user_id not in self.user_ids:
                        continue
                    config_ids = self.env['ace.commission.config'].search([
                        ('type', '=', type),
                        ('trial', '=', user_id.trial)
                    ])
                    amount = 0
                    rate = 0
                    rate_lst = []
                    for cf in config_ids:
                        if rate_lst:
                            rate_lst[-1][2] = cf.total
                        rate_lst += [[cf.rate, cf.total, False, cf.delta_method]] # [rate, min, max, delta method]
                    for rt in rate_lst:
                        if not rt[2]:
                            if not rt[3]:
                                amount = total * rt[0] / 100
                            else:
                                amount += (total - rt[1]) * rt[0] / 100
                            rate = rt[0]
                            break
                        if total < rt[1]:
                            break
                        if total >= rt[2]:
                            amount += rt[2] * rt[0] / 100
                        if total > rt[1] and (not rt[2] or total < rt[2]):
                            if not rt[3]:
                                amount = total * rt[0] / 100
                            else:
                                amount += (total - rt[1]) * rt[0] / 100
                            rate = rt[0]
                            break
                    if not flag:
                        sql_child += """(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                        flag = True
                    else:
                        sql_child += """,(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    # if item != list(data.keys())[-1] or item1 != list(data[item].keys())[-1]:
                    #     sql_child += """, """
                    params_child += [self._uid, self._uid, datetime.now(), datetime.now(), self.id,
                                     item, type, user_id.trial, total, amount, rate, amount]
            if params_child:
                self._cr.execute(sql_child, params_child)


class ACECommissionLine(models.Model):
    _name = 'ace.commission.line'

    user_id = fields.Many2one('res.users', 'Staff')
    job_position = fields.Selection([('sale', 'Salesperson'), ('tels', 'Telesales'), ('ctv', 'CTV')],
                                    string='Job Position')
    trial = fields.Boolean('Trial Work')
    total = fields.Float()
    amount = fields.Float('Commission on Amount')
    rate = fields.Float('Rate(%)')
    commission = fields.Float()
    commission_id = fields.Many2one('ace.commission')

    @api.multi
    def view_invoice(self):
        job = self.job_position == 'tels' and """AND ai.telesales IS NOT NULL""" or \
              (self.job_position == 'ctv' and """AND rsp.job_position = 'ctv'""" or
               """AND COALESCE(rsp.job_position, 'sale') = 'sale'""")
        trial = """AND (rsp.trial = TRUE OR pls.trial = TRUE)"""
        self._cr.execute("""
            SELECT ai.id
            FROM account_invoice ai
                LEFT JOIN res_users sp ON sp.id = ai.user_id
                LEFT JOIN res_partner rsp ON rsp.id = sp.partner_id
                LEFT JOIN res_users tls ON tls.id = ai.telesales
                LEFT JOIN res_partner pls ON pls.id = tls.partner_id
            WHERE ai.state IN ('open', 'in_payment', 'paid')
                  AND ai.type IN ('out_invoice', 'out_refund')
                  AND ai.date_invoice BETWEEN '%s' AND '%s'
                  AND (ai.user_id = %s OR ai.telesales = %s)
                  %s %s
        """ % (self.commission_id.date_from, self.commission_id.date_to, self.user_id.id, self.user_id.id,
               """""" if not self.commission_id.job_position else job, self.commission_id.trial and trial or """"""))
        invoices = self._cr.fetchall()
        invoices = [inv[0] for inv in invoices]
        return {
            'name': _('Invoices'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'views': [(self.env.ref('account.invoice_tree').id, 'tree'),
                      (self.env.ref('account.invoice_form').id, 'form')],
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', invoices or [])],
            'context': "{'type':'out_invoice'}",
            'target': 'target'
        }