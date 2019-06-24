# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        if vals.get('default_code', False) and \
            self.search_count([('default_code', '=', vals.get('default_code', False))]) > 0:
            raise UserError(_("Product code has already existed. Please check again"))
        product_id = super(ProductTemplate, self).create(vals)
        return product_id

    @api.multi
    def write(self, vals):
        if vals.get('default_code', False) and \
                self.search_count([('default_code', '=', vals.get('default_code', False)),
                                   ('id', 'not in', self.ids)]) > 0:
            raise UserError(_("Product code has already existed. Please check again"))
        return super(ProductTemplate, self).write(vals)


class Product(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, vals):
        if vals.get('default_code', False) and \
            self.search_count([('default_code', '=', vals.get('default_code', False))]) > 0:
            raise UserError(_("Product code has already existed. Please check again"))
        product_id = super(Product, self).create(vals)
        return product_id

    @api.multi
    def write(self, vals):
        if vals.get('default_code', False) and \
                self.search_count([('default_code', '=', vals.get('default_code', False)),
                                   ('id', 'not in', self.ids)]) > 0:
            raise UserError(_("Product code has already existed. Please check again"))
        return super(Product, self).write(vals)