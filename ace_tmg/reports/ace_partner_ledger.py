# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

class ACEPartnerLedgerReport(models.TransientModel):
    _inherit = 'ace.partner.ledger.report'

    user_id = fields.Many2one('res.users', 'Salesperson')
    type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor')])

    @api.model
    def default_get(self, fields):
        res = super(ACEPartnerLedgerReport, self).default_get(fields)
        if self._context.get('customer'):
            res.update({'type': 'customer'})
        if self._context.get('supplier'):
            res.update({'type': 'supplier'})
        return res

    def get_report(self):
        journal = self.journal_ids and (len(self.journal_ids) > 1 and
                                        """ AND am.journal_id IN {}""".format(tuple(self.journal_ids.ids)) or
                                        """ AND am.journal_id = {}""".format(self.journal_ids.id)) or """"""
        account = salesperson = """"""
        if self.group_id:
            account_ids = self.env['account.account'].search(
                [('group_id', '=', self.group_id.id)])
            account += account_ids and (len(account_ids) > 1 and
                                        """AND vas.account_id IN {}""".format(tuple(account_ids.ids)) or
                                        """AND vas.account_id = {}""".format(account_ids.id)) or """"""
        if self.account_id:
            account += """AND vas.account_id = {}""".format(self.account_id.id)
        company = self.company_id and """ AND am.company_id = %s""" % self.company_id.id or """"""
        partner = self.partner_ids and (len(self.partner_ids) > 1 and
                                        """ AND rp.id IN {}""".format(tuple(self.partner_ids.ids)) or
                                        """ AND rp.id = {}""".format(self.partner_ids.id)) or """"""
        if self.user_id:
            salesperson = """ AND rp.user_id = {}""".format(self.user_id.id)
        sql = """
            DELETE FROM ace_partner_ledger_line WHERE report_id = {};
            INSERT INTO ace_partner_ledger_line (create_uid, create_date, write_uid, write_date, report_id,
                                                 partner_id, partner_code, partner_name, user_id, debit_start_balance, 
                                                 credit_start_balance, debit, credit, debit_end_balance, credit_end_balance)
                        SELECT {}, '{}', {}, '{}', {}, rp.id, rp.ref, rp.name, rp.user_id,
                               CASE WHEN sb.balance > 0 THEN sb.balance ELSE 0 END debit_start_balance,
                               CASE WHEN sb.balance < 0 THEN sb.balance * -1 ELSE 0 END credit_start_balance,
                               COALESCE(ps.debit, 0) debit, COALESCE(ps.credit, 0) credit,
                               CASE WHEN eb.balance > 0 THEN eb.balance ELSE 0 END debit_end_balance,
                               CASE WHEN eb.balance < 0 THEN eb.balance * -1 ELSE 0 END credit_end_balance
                        FROM res_partner rp
                        LEFT JOIN
                          (SELECT vas.partner_id, SUM(vas.balance) balance
                           FROM account_move_line vas
                               JOIN account_move am ON am.id = vas.move_id
                               JOIN account_journal aj ON aj.id = am.journal_id
                           WHERE 1=1
                                 {}
                                 {}
                                 AND am.state = 'posted'
                                 {}
                                 AND vas.date < '{}'
                           GROUP BY vas.partner_id) sb ON sb.partner_id = rp.id
                        LEFT JOIN
                          (SELECT vas.partner_id,
                                  SUM(vas.balance) balance
                           FROM account_move_line vas
                               JOIN account_move am ON am.id = vas.move_id
                               JOIN account_journal aj ON aj.id = am.journal_id
                           WHERE 1=1
                                 {}
                                 {}
                                 AND am.state = 'posted'
                                 {}
                                 AND vas.date <= '{}'
                           GROUP BY vas.partner_id) eb ON eb.partner_id = rp.id
                        LEFT JOIN
                          (SELECT vas.partner_id,
                                  SUM(vas.debit) debit,
                                  SUM(vas.credit) credit
                           FROM account_move_line vas
                               JOIN account_move am ON am.id = vas.move_id
                               JOIN account_journal aj ON aj.id = am.journal_id
                           WHERE 1=1
                                 {}
                                 {}
                                 AND am.state = 'posted'
                                 {}
                                 AND vas.date BETWEEN '{}' AND '{}'
                           GROUP BY vas.partner_id) ps ON ps.partner_id = rp.id
                        WHERE 1=1 {} {} AND (sb.balance <> 0 OR eb.balance <> 0 OR ps.debit <> 0 OR ps.credit <> 0)
        """.format(self.id, self._uid, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                   self._uid, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                   self.id, account, journal, company, self.date_from,
                   account, journal, company, self.date_to,
                   account, journal, company, self.date_from, self.date_to, partner, salesperson)
        self._cr.execute(sql)


class ACEPartnerLedgerLine(models.TransientModel):
    _inherit = 'ace.partner.ledger.line'

    user_id = fields.Many2one('res.users', 'Salesperson')