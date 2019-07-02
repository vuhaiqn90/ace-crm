# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from calendar import monthrange
from datetime import datetime, timedelta


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    def _create_date_range_seq(self, date):
        if ((self.prefix and ('range_month' in self.prefix or 'range_day' in self.prefix)) or
            (self.suffix and ('range_month' in self.suffix or 'range_day' in self.suffix))) and \
                self.use_date_range:
            year = fields.Date.from_string(date).strftime('%Y')
            month = fields.Date.from_string(date).strftime('%m')
            day = fields.Date.from_string(date).strftime('%d')
            if not 'range_day' in self.prefix and not 'range_day' in self.suffix:
                date_from = '{}-{}-01'.format(year, month)
                date_to = '{}-{}-{}'.format(year, month, monthrange(int(year), int(month))[1])
            else:
                date_from = date_to = '{}-{}-{}'.format(year, month, day)
            date_range = self.env['ir.sequence.date_range'].search \
                ([('sequence_id', '=', self.id), ('date_from', '>=', date), ('date_from', '<=', date_to)],
                 order='date_from desc', limit=1)
            if date_range:
                date_to = datetime.strptime(date_range.date_from, '%Y-%m-%d') + timedelta(days=-1)
                date_to = date_to.strftime('%Y-%m-%d')
            date_range = self.env['ir.sequence.date_range'].search \
                ([('sequence_id', '=', self.id), ('date_to', '>=', date_from), ('date_to', '<=', date)],
                 order='date_to desc', limit=1)
            if date_range:
                date_from = datetime.strptime(date_range.date_to, '%Y-%m-%d') + timedelta(days=1)
                date_from = date_from.strftime('%Y-%m-%d')
            seq_date_range = self.env['ir.sequence.date_range'].sudo().create({
                'date_from': date_from,
                'date_to': date_to,
                'sequence_id': self.id,
            })
            return seq_date_range
        else:
            return super(IrSequence, self)._create_date_range_seq(date)