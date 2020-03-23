# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID


class UtmTerm(models.Model):
    _name = 'utm.term'
    _description = 'UTM Term: Ghi nhận từ khóa hoặc loại sản phẩm chạy quảng cáo. VD: giày thể thao, giày sneaker, ...'
    _order = 'name'

    name = fields.Char(string='Term Name', required=True)
    active = fields.Boolean(default=True)


class UtmContent(models.Model):
    _name = 'utm.content'
    _description = 'UTM Content: Để phân biệt quảng cáo hoặc liên kết trỏ đến cùng một URL. VD: logolink / textlink'
    _order = 'name'

    name = fields.Char(string='Content Name', required=True)
    active = fields.Boolean(default=True)


class UtmMixin(models.AbstractModel):
    _inherit = 'utm.mixin'

    term_id = fields.Many2one('utm.term', 'Term')
    content_id = fields.Many2one('utm.content', 'Content')

    def tracking_fields(self):
        rsl = super(UtmMixin, self).tracking_fields()
        rsl += [
            ('utm_term', 'term_id', 'odoo_utm_term'),
            ('utm_content', 'content_id', 'odoo_utm_content'),
        ]
        return rsl