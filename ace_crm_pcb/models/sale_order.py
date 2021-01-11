# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                name = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'sale.order') or _('New')
            else:
                name = self.env['ir.sequence'].next_by_code('sale.order') or _('New')
            if self.env.user.partner_id.ref:
                name = name.replace('MANV', self.env.user.partner_id.ref)
            vals['name'] = name
        if vals.get('default_code', False) and \
            self.search_count([('default_code', '=', vals.get('default_code', False))]) > 0:
            raise UserError(_("Product code has already existed. Please check again"))
        product_id = super(SaleOrder, self).create(vals)
        return product_id

    @api.multi
    def get_payment_term(self, lang='vn'):
        if self.payment_term_id and self.payment_term_id.note:
            term = self.payment_term_id.note.split('\n')
            if term:
                if lang == 'vn' or not lang:
                    return term[0]
                else:
                    return term[1]
        return ''


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Overwrite core function
    def _purchase_service_create(self, quantity=False):
        """ On Sales Order confirmation, some lines (services ones) can create a purchase order line and maybe a purchase order.
            Create a RFQ. The created purchase order line will be linked to the SO line.
            :param quantity: the quantity to force on the PO line, expressed in SO line UoM
        """
        PurchaseOrder = self.env['purchase.order']
        supplier_po_map = {}
        sale_line_purchase_map = {}
        for line in self:
            line = line.with_context(force_company=line.company_id.id)
            # determine vendor of the order (take the first matching company and product)
            # VFE fixme why isn't the _select_seller function used ???
            suppliers = line.product_id.seller_ids.filtered(lambda vendor: (not vendor.company_id or vendor.company_id == line.company_id) and (not vendor.product_id or vendor.product_id == line.product_id))
            if not suppliers:
                raise UserError(_("There is no vendor associated to the product %s. Please define a vendor for this product.") % (line.product_id.display_name,))
            supplierinfo = suppliers[0]
            partner_supplier = supplierinfo.name  # yes, this field is not explicit .... it is a res.partner !

            # determine (or create) PO
            # purchase_order = supplier_po_map.get(partner_supplier.id)
            # if not purchase_order:
            #     purchase_order = PurchaseOrder.search([
            #         ('partner_id', '=', partner_supplier.id),
            #         ('state', '=', 'draft'),
            #         ('company_id', '=', line.company_id.id),
            #     ], limit=1)
            # if not purchase_order:
            values = line._purchase_service_prepare_order_values(supplierinfo)
            purchase_order = PurchaseOrder.create(values)
            # else:  # update origin of existing PO
            #     so_name = line.order_id.name
            #     origins = []
            #     if purchase_order.origin:
            #         origins = purchase_order.origin.split(', ') + origins
            #     if so_name not in origins:
            #         origins += [so_name]
            #         purchase_order.write({
            #             'origin': ', '.join(origins)
            #         })
            supplier_po_map[partner_supplier.id] = purchase_order

            # add a PO line to the PO
            values = line._purchase_service_prepare_line_values(purchase_order, quantity=quantity)
            purchase_line = line.env['purchase.order.line'].create(values)

            # link the generated purchase to the SO line
            sale_line_purchase_map.setdefault(line, line.env['purchase.order.line'])
            sale_line_purchase_map[line] |= purchase_line
        return sale_line_purchase_map