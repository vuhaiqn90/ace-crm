from odoo import fields,api,models
class MakeInvoice(models.TransientModel):
    _name = 'confirm.room'
    _description = 'Confirm Room'

    @api.multi
    def continue_booking(self):
        ctx = dict(self._context or {})
        ctx.update({'continue_booking':True})
        return self.env['tour.hotel.reservation'].browse(ctx.get('active_id')).with_context(ctx).make_booking()

    @api.multi
    def cancel_booking(self):
        ctx = dict(self._context or {})
        ctx.update({'cancel_booking':True})
        return self.env['tour.hotel.reservation'].browse(ctx.get('active_id')).with_context(ctx).make_booking()