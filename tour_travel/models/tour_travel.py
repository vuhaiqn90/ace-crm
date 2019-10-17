import time
from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, Warning
import datetime
from datetime import datetime, timedelta
from odoo.fields import Many2one


def get_price(self, pricelist_ids, price):
    pricelist_item_ids = []
    if self._context is None:
        self._context = {}

    date = time.strftime('%Y-%m-%d')
    if 'date' in self._context:
        date = self._context['date']

    currency_obj = self.env['res.currency']
    product_pricelist_version_obj = self.env['product.pricelist.item']
    user_browse = self.env['res.users'].browse(self._uid)
    company_id = user_browse.company_id
    pricelist_obj = self.env['product.pricelist'].browse(pricelist_ids)
    if pricelist_ids:
        pricelist_item_ids.append(pricelist_ids)

    pricelist_item_ids = list(set(pricelist_item_ids))
    plversions_search_args = [
        ('pricelist_id', 'in', pricelist_item_ids),
        '|',
        ('date_start', '=', False),
        ('date_start', '<=', date),
        '|',
        ('date_end', '=', False),
        ('date_end', '>=', date),
    ]
    plversion_ids = product_pricelist_version_obj.search(plversions_search_args)

    if not plversion_ids:
        msg = "At least one pricelist item has not declared !\nPlease create pricelist item."
        raise Warning(msg)

    self._cr.execute(
        'SELECT i.* '
        'FROM product_pricelist_item AS i '
        'WHERE id = ' + str(plversion_ids[0].id) + '')

    res1 = self._cr.dictfetchall()
    if pricelist_obj:
        price = currency_obj.compute(price, pricelist_obj.currency_id,round=False)
    for res in res1:
        if res:
            price_limit = price
            x = (1.0 + (res['price_discount'] or 0.0))
            price = price * (1.0 + (res['price_discount'] or 0.0))
            price += (res['price_surcharge'] or 0.0)
            if res['price_min_margin']:
                price = max(price, price_limit + res['price_min_margin'])
            if res['price_max_margin']:
                price = min(price, price_limit + res['price_max_margin'])
            break

    price_amt = price
    return price_amt


# def get_price(self, cr, uid, ids, pricelist_ids, price, context=None):
#     price_amt = 0.0
#     pricelist_item_ids = []
#     if context is None:
#         context = {}
# 
#     date = time.strftime('%Y-%m-%d')
#     if 'date' in context:
#         date = context['date']
#                     
#     currency_obj = self.pool.get('res.currency')
#     product_pricelist_version_obj = self.pool.get('product.pricelist.item')
#     user_browse = self.pool.get('res.users').browse(cr, uid, uid)
#     company_obj = self.pool.get('res.company')
#     company_id = company_obj.browse(cr, uid, user_browse.company_id.id)
#     print(company_id, "company_id")
# #    print company_id.currency_id.id ,"company_idccccc"
#     pricelist_obj = self.pool.get('product.pricelist').browse(cr, uid, pricelist_ids)
#     if pricelist_ids:
#         pricelist_item_ids.append(pricelist_ids)
#         pricelist_obj = self.pool.get('product.pricelist').browse(cr, uid, pricelist_ids)
#         
#     pricelist_item_ids = list(set(pricelist_item_ids))
#     plversions_search_args = [
#         ('pricelist_id', 'in', pricelist_item_ids),
#         '|',
#         ('date_start', '=', False),
#         ('date_start', '<=', date),
#         '|',
#         ('date_end', '=', False),
#         ('date_end', '>=', date),
#     ]
#     print(plversions_search_args,"plversions_search_args---------------")
#     plversion_ids = product_pricelist_version_obj.search(cr, uid, plversions_search_args)
#     print(plversion_ids,"plversion_ids------------")
#     # # commit becouse product_pricelist_version object removed from odoo 9 .................
# #     if len(pricelist_item_ids) != len(plversion_ids):
# #         msg = "At least one pricelist has no active version !\nPlease create or activate one."
# #         raise osv.except_osv(_('Warning !'), _(msg))
#     
#     if not plversion_ids:
#         msg = "At least one pricelist item has not declared !\nPlease create pricelist item."
#         raise Warning(msg)
#     
# #     cr.execute(
# #                 'SELECT i.*, pl.currency_id '
# #                 'FROM product_pricelist_item AS i, '
# #                     'product_pricelist_version AS v, product_pricelist AS pl '
# #                 'WHERE price_version_id = '+str(plversion_ids[0])+''
# #                     'AND i.price_version_id = v.id AND v.pricelist_id = pl.id ')
#     cr.execute(
#                 'SELECT i.* '
#                 'FROM product_pricelist_item AS i '
#                 'WHERE id = ' + str(plversion_ids[0]) + '')
# 
#     
#                 
#     res1 = cr.dictfetchall()
#     print(res1, "res1")
#     if pricelist_obj:
#         print(pricelist_obj, "pricelist_obj")
#         print(pricelist_obj.currency_id.id, "pricelist_obj.currency_id.id")
#         print(price, "pricelist_obj.cprivee")
#         price = currency_obj.compute(cr, uid, company_id.currency_id.id, pricelist_obj.currency_id.id, price, round=False)
#         print(price, "price")
#     for res in res1:
#         if res:
#             price_limit = price
#             x = (1.0 + (res['price_discount'] or 0.0))
#             price = price * (1.0 + (res['price_discount'] or 0.0))
#             price += (res['price_surcharge'] or 0.0)
#             if res['price_min_margin']:
#                 price = max(price, price_limit + res['price_min_margin'])
#             if res['price_max_margin']:
#                 price = min(price, price_limit + res['price_max_margin'])
#             break
# 
#     price_amt = price
#     return price_amt


class product_category(models.Model):
    _inherit = "product.category"
    _description = "Product Category"

    @api.multi
    def unlink(self):
        """
        Allows to delete Product Category which are not defined in demo data
        """
        for rec in self:
            if rec.id in [1, 2, 3, 4, 5, 6, 7, 8]:
                raise Warning('Cannot delete these Product Category. !')
        return super(product_category, self).unlink()


#     def unlink(self, cr, uid, ids, context):
#         """
#         Allows to delete Product Category which are not defined in demo data
#         """
#         for rec in self.browse(cr, uid, ids, context=context):
#             if rec.id in [1, 2, 3, 4, 5, 6, 7, 8]:
#                 raise osv.except_osv(_('Invalid action !'), _('Cannot delete these Product Category. !'))
#         return super(product_category, self).unlink(cr, uid, ids, context=context)


class tour_package_type(models.Model):
    _name = "tour.package.type"
    _description = "Tour Package Types"

    name = fields.Char('Tour Package', size=164, required=True)
    code = fields.Char('Package Code', size=164, required=True)


class tour_season(models.Model):
    _name = "tour.season"
    _description = "Tour Seasons"

    name = fields.Char('Season', size=164, required=True)
    code = fields.Char('Code', size=164, required=True)


class tour_destinations(models.Model):
    _name = "tour.destinations"
    _description = "Tour Destinations"

    name = fields.Char('Destination Name', size=164, required=True)
    country_id = fields.Many2one('res.country', string='Country')
    code = fields.Char('Code', size=164, required=True)


class tour_facility(models.Model):
    _name = "tour.facility"
    _description = "Tour Facility"

    name = fields.Char('Facility Name', size=164, required=True)
    code = fields.Char('Code', size=10, required=True)
    desc = fields.Char('Description', size=256)


class tour_payment_policy(models.Model):
    _name = "tour.payment.policy"
    _description = "Tour Payment Policies for Customer"

    @api.model
    def create(self, vals):
        if 'before_book_date_perc' in vals:
            vals['before_pay_date_perc'] = 100 - vals['before_book_date_perc']
        return super(tour_payment_policy, self).create(vals)

    #     def create(self, cr, uid, vals, *args, **kwargs):
    #         if 'before_book_date_perc' in vals:
    #             vals['before_pay_date_perc'] = 100 - vals['before_book_date_perc']
    #         return super(tour_payment_policy, self).create(cr, uid, vals, *args, **kwargs)

    @api.multi
    def write(self, vals):
        if 'before_book_date_perc' in vals:
            vals['before_pay_date_perc'] = 100 - vals['before_book_date_perc']
        return super(tour_payment_policy, self).write(vals)

    #     def write(self, cr, uid, ids, vals, context={}):
    #         if 'before_book_date_perc' in vals:
    #             vals['before_pay_date_perc'] = 100 - vals['before_book_date_perc']
    #         return super(tour_payment_policy, self).write(cr, uid, ids, vals, context)

    name = fields.Char('Policy Name', size=164, requierd=True)
    before_book_date_perc = fields.Integer('Payment Percentage Before Booking Date', required=True)
    before_pay_date_perc = fields.Integer('Payment Percentage After Booking Date')

    @api.onchange('before_book_date_perc')
    def on_change_book_date_percentage(self):
        result = {}
        result['before_pay_date_perc'] = 100 - self.before_book_date_perc
        return {'value': result}


#     def on_change_book_date_percentage(self, cr, uid, ids, before_book_date_perc):
#         result = {}
#         result['before_pay_date_perc'] = 100 - before_book_date_perc
#         return {'value':result}


class tour_deduction_policy(models.Model):
    _name = "tour.deduction.policy"
    _description = "tour_deduction_policy"

    name = fields.Integer('Minimum Limit (days)', required=True)
    max_limit = fields.Integer('Maximum Limit (days)', required=True)
    deduction_percentage = fields.Float("Deduction Percentage", required=True)


class tour_package(models.Model):
    _name = "tour.package"
    _description = "Tour Package"
    _rec_name = "name1"

    def button_dummy(self):
        return True

    #     def button_dummy(self, cr, uid, ids, context=None):
    #         return True

    def _get_total_amt(self):
        res = {}
        transport_total = 0
        for obj in self:
            if obj.transport_line_ids:
                for transport_line in obj.transport_line_ids:
                    transport_total = transport_total + transport_line.total_amt

        res[obj.id] = transport_total
        return res

    #     def _get_total_amt(self, cr, uid, ids, args1, args2, context=None):
    #         res = {}
    #         transport_total = 0
    #         service_total = 0
    #         for obj in self.browse(cr, uid, ids):
    #             if obj.transport_line_ids:
    #                 for transport_line in obj.transport_line_ids:
    #                     transport_total = transport_total + transport_line.total_amt
    #
    #         res[obj.id] = transport_total
    #         return res

    def _get_individual_cost_price(self):
        res = {}
        price = 0
        cost = 0
        person = 0
        for obj in self:
            if obj.cost_price and obj.number_of_person:
                cost = int(obj.cost_price)
                person = int(obj.number_of_person)
                price = cost / person
        res[obj.id] = price
        return res

    #     def _get_individual_cost_price(self, cr, uid, ids, args1, args2, context=None):
    #         res = {}
    #         price = 0
    #         cost = 0
    #         person = 0
    #         for obj in self.browse(cr, uid, ids):
    #             if obj.cost_price and obj.number_of_person:
    #                 cost = int(obj.cost_price)
    #                 person = int(obj.number_of_person)
    #                 price = cost / person
    #         res[obj.id] = price
    #         return res

    def get_user_info(self, vals):

        user_obj = self.env['res.users'].browse(self._uid)
        partner_obj = self.env['res.partner'].browse([self._uid])
        return {'value': {'company': partner_obj[0].name,
                          'website': partner_obj[0].website,
                          'user_name': user_obj[0].name,
                          }
                }

    #     def get_user_info(self, cr, uid, ids, vals, context=None):
    #
    #         user_obj = self.pool.get('res.users').browse(cr, uid, [uid])
    #         user_name = user_obj[0].name
    #         partner_obj = self.pool.get('res.partner').browse(cr, uid, [uid])
    #         return {'value':{'company':partner_obj[0].name,
    #                          'website':partner_obj[0].website,
    #                          'user_name':user_obj[0].name,
    #                          }
    #                 }

    def _amount_all(self):
        res = {}
        if self._context is None:
            self._context = {}

        sub_total = 0.0
        tot_with_tax = 0.0
        total_tax = 0.0
        records = self
        for line in records[0].product_line_id:
            price = line.price_unit
            taxes = line.tax_id.compute_all(price, None, line.qty, line.product_id)

            """
                The tax_obj.compute_all method returns the following dictionary..........
        RETURN: {
                    'total': 0.0,                # Total without taxes
                    'total_included: 0.0,        # Total with taxes
                    'taxes': []                  # List of taxes, see compute for the format
                }
        """
            sub_total = sub_total + taxes['total_excluded']
            tot_with_tax = tot_with_tax + taxes['total_included']
            if taxes['taxes']:
                for tax in taxes['taxes']:
                    total_tax = total_tax + tax['amount']

        res[records[0].id] = {
            'subtotal': 0.0,
            #                 'total_amt': 0.0,
            #                 'tax_amt': 0.0,
        }
        res[records[0].id]["subtotal"] = sub_total

    #         res[records[0].id]["total_amt"] = tot_with_tax
    #         res[records[0].id]["tax_amt"] = tot_with_tax - sub_total
    # return res

    #     def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
    #         tax_obj = self.pool.get('account.tax')
    #         res = {}
    #         if context is None:
    #             context = {}
    #
    #         sub_total = 0.0
    #         tot_with_tax = 0.0
    #         total_tax = 0.0
    #         records = self.browse(cr, uid, ids, context=context)
    #         for line in records[0].product_line_id:
    #             price = line.price_unit
    #             taxes = line.tax_id.compute_all(price, None, line.qty, line.product_id)
    #
    #             """
    #                 The tax_obj.compute_all method returns the following dictionary..........
    #         RETURN: {
    #                     'total': 0.0,                # Total without taxes
    #                     'total_included: 0.0,        # Total with taxes
    #                     'taxes': []                  # List of taxes, see compute for the format
    #                 }
    #         """
    #             sub_total = sub_total + taxes['total_excluded']
    #             tot_with_tax = tot_with_tax + taxes['total_included']
    #             if taxes['taxes']:
    #                 for  tax in taxes['taxes']:
    #                     total_tax = total_tax + tax['amount']
    #
    #
    #
    #         res[records[0].id] = {
    #                 'subtotal': 0.0,
    #                 'total_amt': 0.0,
    #                 'tax_amt': 0.0,
    #             }
    #         res[records[0].id]["subtotal"] = sub_total
    #         res[records[0].id]["total_amt"] = tot_with_tax
    #         res[records[0].id]["tax_amt"] = tot_with_tax - sub_total
    #         return res

    def _get_order(self):
        result = {}
        for line in self:
            result[line.tour_package_id.id] = True
        return list(result.keys())

    #     def _get_order(self, cr, uid, ids, context=None):
    #         result = {}
    #         for line in self.pool.get('tour.package.products.line').browse(cr, uid, ids, context=context):
    #             result[line.tour_package_id.id] = True
    #         return list(result.keys())

    name1 = fields.Char("Tour Name", size=256)
    product_id = fields.Many2one('product.product', 'Tour Name', required=True)
    # code = fields.Char("Tour Code", size=100)
    tour_date_lines = fields.One2many('tour.dates', 'tour_id', 'Tour date Lines')
    tour_programme_lines = fields.One2many('tour.programme', 'tour_id1', 'Tour Programme Lines')
    tour_destination_lines = fields.One2many('tour.destination.line', 'tour_id', 'Tour Destination Lines')
    tour_cost_include_facility_lines = fields.One2many('tour.cost.include.facility', 'tour_id',
                                                       'Tour Cost Included Facility Lines')
    tour_cost_exclude_facility_lines = fields.One2many('tour.cost.exclude.facility', 'tour_id',
                                                       'Tour Cost Excluded Facility Lines')
    tour_road_travel_lines = fields.One2many('tour.road.travel', 'tour_id', 'Tour Road Travel Lines')
    tour_hotel_info_lines = fields.One2many('tour.destination.hotel.line', 'tour_id', 'Tour Hotel Info Lines')
    current_date = fields.Date("Date of Publish", required=True)
    days = fields.Selection([
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'),
        ('10', '10'),
        ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'),
        ('19', '19'), ('20', '20'),
        ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24'), ('25', '25'), ('26', '26'), ('27', '27'), ('28', '28'),
        ('29', '29'), ('30', '30')
    ], 'Days', required=True)
    tour_type = fields.Selection([
        ('international', 'International'),
        ('domestic', 'Domestic')
    ], "Tour Type", required=True)
    tour_category = fields.Selection([
        ('package', 'Packaged Tour'),
        ('custom', 'Custom Tour')
    ], "Tour Category", required=True, default=lambda *a: 'package')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('checkout', "Checkout"),
        ('cancel', 'Canceled'),
        ('done', 'Done')
    ], 'Status', readonly=True, default=lambda *a: 'draft')
    tour_booking_customer_ids = fields.Many2many('tour.booking', 'tour_booking_customer_rel',
                                                 'tour_booking_customer_id', 'tour_id',
                                                 'Tour Customer Booking', readonly=True)
    tour_intro = fields.Text('Introduction')
    user_name = fields.Char('user', size=64, store=False)
    company = fields.Char('company', size=64, store=False)
    website = fields.Char('website', size=64, store=False)
    product_line_id = fields.One2many('tour.package.products.line', 'tour_package_id', 'Product')

    subtotal = fields.Float(string='Subtotal', multi='sums', help="Subtotal")

    tax_amt = fields.Float(string='Total Taxed Amount', multi='sums', help="Total Taxed Amount")

    total_amt = fields.Float(string='Total Amount', multi='sums', help="Total Amount Including Tax")

    #     _defaults = {
    #                  'state': lambda *a: 'draft',
    #                  'tour_category': lambda *a: 'package',
    #                  }

    @api.onchange('product_id')
    def on_change_product_idoo1(self):
        kk = ''
        if self.product_id:
            kk = self.product_id.name
        return {'value': {'name1': kk}}

    #     def on_change_product_idoo1(self, cr, uid, ids, product_id):
    #         kk = ''
    #         if product_id:
    #             obj = self.pool.get('product.product').browse(cr, uid, product_id)
    #             kk = obj.name
    #         return {'value': {'name1': kk}}

    @api.multi
    def button_confirm(self):
        obj = self
        if not (obj[0].tour_date_lines and obj[0].tour_programme_lines and obj[0].tour_destination_lines and
                obj[0].tour_cost_include_facility_lines and obj[0].tour_cost_exclude_facility_lines):
            raise UserError('Data Error ! Please fill all Details related to tour')
        return self.write({'state': 'confirm'})


#     def button_confirm(self, cr, uid, ids, context=None):
#         obj = self.browse(cr, uid, ids)
#         if not (obj[0].tour_date_lines and obj[0].tour_programme_lines and obj[0].tour_destination_lines and 
#                 obj[0].tour_cost_include_facility_lines and obj[0].tour_cost_exclude_facility_lines):
#             raise osv.except_osv('Data Error !', 'Please fill all Details related to tour')
#         return self.write(cr, uid, ids, {'state':'confirm'})


class tour_dates(models.Model):
    _name = "tour.dates"
    _description = "Tour dates"

    name = fields.Char('Tour Date', size=100, readonly=True, states={'draft': [('readonly', False)]})
    season_id = fields.Many2one('tour.season', "Season", required=True, readonly=True,
                                states={'draft': [('readonly', False)]})
    start_date = fields.Date("Start Date", required=True, readonly=True, states={'draft': [('readonly', False)]})
    book_date = fields.Date("Last Date of Booking", required=True, readonly=True,
                            states={'draft': [('readonly', False)]})
    due_date = fields.Date("Payment Due Date", required=True, readonly=True, states={'draft': [('readonly', False)]})
    total_seat = fields.Integer("Total Seats", required=True, readonly=True, states={'draft': [('readonly', False)]})
    available_seat = fields.Integer("Available Seats", required=True, readonly=True,
                                    states={'draft': [('readonly', False)]})
    adult_cost_price = fields.Float('Adults Cost Per Person', required=True, readonly=True,
                                    states={'draft': [('readonly', False)]})
    child_cost_price = fields.Float('Child Cost Per Person', required=True, readonly=True,
                                    states={'draft': [('readonly', False)]})
    tour_id = fields.Many2one('tour.package', 'Tour ID', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('available', 'Available'),
        ('closed', "Closed"),
        ('reopen', 'Reopen'),
    ], 'Status', readonly=True, default=lambda *a: 'draft')

    #     _defaults = {
    #                  'state': lambda *a: 'draft',
    #                  }

    @api.onchange('start_date')
    def onchange_tour_date(self):
        result = {}
        if self.start_date:
            fmt = '%Y-%m-%d'
            t_date =(self.start_date)
            month_list = ("", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
            x = str(t_date.day) + '-' + month_list[t_date.month] + '-' + str(t_date.year)
            
            str_name = x
            result['name'] = str_name
        return {'value': result}

    #     def onchange_tour_date(self, cr, uid, ids, tour_date):
    #         result = {}
    #         if tour_date:
    #             print("tour date type", type(tour_date))
    #             fmt = '%Y-%m-%d'
    #             t_date = datetime.strptime(tour_date, fmt)
    #             month_list = ("", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
    #             x = str(t_date.day) + '-' + month_list[t_date.month] + '-' + str(t_date.year)
    #             str_name = x
    #             print('str_name', str_name)
    #             result['name'] = str_name
    #
    #         return {'value':result}

    @api.multi
    def confirm_tour(self):
        for obj in self:
            if (obj.start_date <= obj.book_date):
                raise Warning('Tour Start Date should be greater than Booking Date.')
            if (obj.due_date > obj.book_date):
                raise Warning('Payment Due Date should be less than or equal to Last Date of Booking.')

        self.write({'state': 'available'})
        return True

    #     def confirm_tour(self, cr, uid, ids, *args):
    #         for obj in self.browse(cr, uid, ids):
    #             if (obj.due_date < obj.book_date):
    #                 raise osv.except_osv(_('Error !'), _('Payment Due Date should not be less than Last Date of Booking.'))
    #             if (obj.due_date > obj.start_date):
    #                 raise osv.except_osv(_('Error !'), _('Payment Due Date should not be greater than Tour Start Date.'))
    #         self.write(cr, uid, ids, {'state':'available'})
    #         return True

    def open_tour(self):
        self.write({'state': 'closed'})
        return True

    #     def open_tour(self, cr, uid, ids, *args):
    #         self.write(cr, uid, ids, {'state':'closed'})
    #         return True

    def reopen_tour(self):
        self.write({'state': 'draft'})
        return True


#     def reopen_tour(self, cr, uid, ids, *args):
#         self.write(cr, uid, ids, {'state':'draft'})
#         return True          


class tour_programme(models.Model):
    _name = "tour.programme"
    _description = "Tour Programme"

    name = fields.Char('Days', size=164, required=True)
    description = fields.Text('Description', required=True)
    breakfast = fields.Boolean('Breakfast')
    lunch = fields.Boolean('Lunch')
    dinner = fields.Boolean('Dinner')
    tour_id1 = fields.Many2one('tour.package', 'Tour ID')


class tour_destination_line(models.Model):
    _name = "tour.destination.line"
    _description = "Tour Destination Lines"

    destination_id = fields.Many2one('tour.destinations', 'Destination', required=True)
    country_id = fields.Many2one('res.country', 'Country', required=True)
    name = fields.Integer('No. Of Nights', required=True)
    tour_id = fields.Many2one('tour.package', 'Tour ID')
    is_visa = fields.Boolean('Is Visa Required')
    visa_type = fields.Selection(
        [('single', 'Tourist Visa(Single Entry)'), ('multiple', 'Tourist Visa(Multiple Entry)')], "Visa Type")
    hotel_lines = fields.One2many('tour.destination.hotel.line', 'destination_line_id', 'Destination Hotels')

    @api.onchange('destination_id')
    def onchange_destination_id(self):
        result = {}
        if self.destination_id:
            result['country_id'] = self.destination_id.country_id.id
        return {'value': result}


#     def onchange_destination_id(self, cr, uid, ids, destination_id):
#         result = {}
#         if destination_id:
#             obj = self.pool.get('tour.destinations').browse(cr, uid, destination_id)
#             result['country_id'] = obj.country_id.id     
#         return {'value':result}


# @api.onchange('hotel_lines')
# def _onchnage_hotel_lines(self):
#


class tour_destination_hotel_line(models.Model):
    _name = "tour.destination.hotel.line"
    _description = "Tour Destination Hotel Lines"

    @api.model
    def create(self, vals):
        """
        To override create method
        """

        if 'destination_line_id' in vals:
            if vals['destination_line_id']:
                obj_tour = self.env['tour.destination.line'].browse(vals['destination_line_id'])
                vals.update({'tour_id': obj_tour.tour_id.id})
        return super(tour_destination_hotel_line, self).create(vals)

    #     def create(self, cr, uid, vals, context=None):
    #         """
    #         To override create method
    #         """
    #
    #         if vals.__contains__('destination_line_id'):
    #             if vals['destination_line_id']:
    #                 obj_tour = self.pool.get('tour.destination.line').browse(cr, uid, vals['destination_line_id'])
    #                 vals.update({'tour_id': obj_tour.tour_id.id})
    #         return super(tour_destination_hotel_line, self).create(cr, uid, vals)

    destination_line_id = fields.Many2one('tour.destination.line', 'Destination Id', required=True)
    hotel_type_id = fields.Many2one('hotel.type', 'Hotel Type', required=True)
    hotel_id = fields.Many2one('res.partner', 'Hotel', required=True, )
    room_type_id = fields.Many2one('product.product', "Room Type", required=True, )
    name = fields.Boolean('Primary')
    tour_id = fields.Many2one('tour.package', 'Tour ID')

    @api.onchange('hotel_id')
    def onchange_hotelid(self):
        if self.hotel_id and not self.hotel_type_id:
            raise Warning("Please select Hotel Type first")

        elif self.hotel_id:
            product_ids = []
            hotel_type_ids = self.env['hotel.information'].search(
                [('hotel_id', '=', self.hotel_id.id), ('state', '=', 'confirm')])
            # tour_ids_with_same_season = []

            for room_type in hotel_type_ids.room_info_ids:

                room_ids = self.env['product.template'].search([('name', '=', room_type.name)])
                print(hotel_type_ids.room_info_ids)
                # for cost_price1 in hotel_type_ids.room_info_ids:
                #       print (cost_price1.cost_price)
                print(room_ids)
                for product in room_ids:
                    product_ids.append(product.id)
                print(product_ids)
            # room_in_same_hotel.append(room_type.id)
            # print (room_in_same_hotel)

            # return roomtyp['AC','NONAC']
            #                 [tour_ids_with_same_season.append(line.tour_id.id) for line in tour.tour_date_lines if line.season_id.id==self.season_id.id]
            #         #print (tour_ids_with_same_season)
            return {
                'domain': {
                    'room_type_id': [('id', 'in', product_ids)]
                }
            }


class provider_information_line(models.Model):
    _name = "provider.information.line"
    _description = "Provider Information Line"

    provider_id = fields.Many2one('transport.information', 'Service Provider', required=True)
    name = fields.Boolean('Primary')
    transport_carrier_id = fields.Many2one('transport.carrier', 'Carrier Name', required=True)
    ref_id1 = fields.Many2one('tour.road.travel', 'Service Provider', required=True)


class travel_class(models.Model):
    _name = 'travel.class'
    _description = 'Travel Class'

    name = fields.Char('Travel Class', size=64, required=True)
    code = fields.Char('Travel Class Code', size=64)
    transport_type_id = fields.Many2one('product.product', 'Transport Type', required=True)


class tour_road_travel(models.Model):
    _name = "tour.road.travel"
    _description = "Tour Road Travel Details"

    from_destination_id = fields.Many2one('tour.destinations', 'From', required=True)
    to_destination_id = fields.Many2one('tour.destinations', 'To', required=True)
    name = fields.Integer('Distance in KM', required=True)
    approx_time = fields.Float('Time(Hrs)', required=True)
    tour_id = fields.Many2one('tour.package', 'Tour ID')
    transport_type_id = fields.Many2one('product.product', 'Transport Type', required=True)
    travel_class_id = fields.Many2one('travel.class', 'Travel Class', required=True)
    provider_ids = fields.One2many('provider.information.line', 'ref_id1', 'Provider Details')


class tour_cost_included_facility(models.Model):
    _name = "tour.cost.include.facility"
    _description = "Tour Cost Include Facility"

    @api.onchange('facility_id')
    def onchange_facility(self):
        kk = ''
        if self.facility_id:
            kk = self.facility_id.desc
        return {'value': {'name': kk}}

    #     def onchange_facility(self, cr, uid, ids, facility_id):
    #         kk = ''
    #         if facility_id:
    #             obj = self.pool.get('tour.facility').browse(cr, uid, facility_id)
    #             kk = obj.desc
    #         return {'value': {'name': kk}}

    facility_id = fields.Many2one('tour.facility', 'Facility', required=True)
    name = fields.Char('Description', size=164, required=True)
    tour_id = fields.Many2one('tour.package', 'Tour ID')


class tour_cost_exclude_facility(models.Model):
    _name = "tour.cost.exclude.facility"
    _description = "Tour Cost Exclude Facility"

    @api.onchange('facility_id')
    def onchange_facility(self):
        kk = ''
        if self.facility_id:
            kk = self.facility_id.desc
        return {'value': {'name': kk}}

    #     def onchange_facility(self, cr, uid, ids, facility_id):
    #         kk = ''
    #         if facility_id:
    #             obj = self.pool.get('tour.facility').browse(cr, uid, facility_id)
    #             kk = obj.desc
    #         return {'value': {'name': kk}}

    facility_id = fields.Many2one('tour.facility', 'Facility', required=True)
    name = fields.Char('Description', size=164, required=True)
    tour_id = fields.Many2one('tour.package', 'Tour ID')


class tour_hotel_info(models.Model):
    _name = "tour.hotel.info"
    _description = "Tour Hotel Information"

    hotel_id = fields.Many2one('res.partner', 'Hotel', required=True)
    name = fields.Char('Code', size=164, required=True)
    hotel_customer_booking_lines = fields.One2many('tour.hotel.customer.book', 'hotel_info_id',
                                                   'Tour Hotel Customer Booking Lines')
    attachment_ids = fields.One2many('ir.attachment', 'hotel_customer_id', 'Attachment Lines')
    tour_id = fields.Many2one('tour.package', 'Tour ID')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', "Canceled"),
    ], 'Status', readonly=True, default=lambda *a: 'draft')

    #     _defaults = {
    #                  'state': lambda *a: 'draft',
    #                  }

    @api.multi
    def confirm(self):
        self.write({'state': 'confirm'})
        return True


#     def confirm(self, cr, uid, ids, *args):
#         self.write(cr, uid, ids, {'state':'confirm'})
#         return True          


class tour_hotel_customer_book(models.Model):
    _name = "tour.hotel.customer.book"
    _description = "Hotel Customer Booking Lines "

    partner_id = fields.Many2one('res.partner', "Customer")
    name = fields.Integer('Adults')
    childs = fields.Integer('Child')
    hotel_info_id = fields.Many2one('tour.hotel.info', 'Hotel Ref')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('wait', 'In Process'),
        ('booked', 'Booked'),
        ('cancel', "Canceled"),
    ], 'Status', readonly=True, default=lambda *a: 'draft')

    #     _defaults = {
    #                  'state': lambda *a: 'draft',
    #                  }

    @api.multi
    def button_request(self):
        self.write({'state': 'wait'})
        return True

    #     def button_request(self, cr, uid, ids, *args):
    #         self.write(cr, uid, ids, {'state':'wait'})
    #         return True

    @api.multi
    def button_confirm(self):
        self.write({'state': 'booked'})
        return True


#     def button_confirm(self, cr, uid, ids, *args):
#         self.write(cr, uid, ids, {'state':'booked'})
#         return True


class tour_package_info(models.Model):
    _name = "tour.package.info"
    _description = "Tour Package info"

    package_type_id = fields.Many2one('tour.package.type', 'Package', required=True)
    name = fields.Selection([
        ('international', 'International'),
        ('domestic', 'Domestic')
    ], "Tour Type", required=True)
    tour_line_ids = fields.Many2many('tour.package', 'tour_package_rel', 'package_id', 'tour_id', 'Tour Information')






class tour_booking(models.Model):
    _name = "tour.booking"

    _description = "Tour Booking"

    def get_partner_lang_dates(self, date1, lang):
        record = self.env['res.lang'].search([('code', '=', lang)])
        new_datetime = ''
        if len(str(date1)) > 11:
            new_date = str(date1.date())
            new_time =datetime.strftime(datetime.strptime(str(date1), '%Y-%m-%d %H:%M:%S'), '%H:%M:%S')
            new_datetime = str(new_date) + " " + str(new_time)
        else:
            new_date =datetime.strptime(str(date1), '%Y-%m-%d')
            new_datetime = str(new_date)

        return new_datetime

    #     def get_partner_lang_dates(self, cr, uid, ids, date1,lang):
    #         search_id = self.pool.get('res.lang').search(cr,uid,[('code','=',lang)])
    #         record=self.pool.get('res.lang').browse(cr,uid,search_id)
    #         new_datetime = ''
    #         if len(date1) > 11:
    #             print('Time')
    #             new_date=datetime.strftime(datetime.strptime(date1,'%Y-%m-%d %H:%M:%S'),record.date_format)
    #             new_time=datetime.strftime(datetime.strptime(date1,'%Y-%m-%d %H:%M:%S'),'%H:%M:%S')
    #             print('*Time',new_time)
    #             new_datetime = new_date + " " + new_time
    #         else:
    #             print('Date only')
    #             new_date=datetime.strftime(datetime.strptime(date1,'%Y-%m-%d'),record.date_format)
    #             new_datetime = new_date
    #         print("!!!!!!!!!!!!!!!!---new date=",new_datetime)
    #
    #         return new_datetime

    def get_transport_information(self, object):
        booking_id = self.env['transport.book'].search([('tour_book_id', '=', object.id)])
        final_res = {}
        result_acc = []
        cus_res = {}
        for booking in booking_id:
            address = ''
            res = []
            seq = 1
            for customer in booking.customer_line_ids:
                if customer.gender == 'male':
                    gender = 'M'
                else:
                    gender = 'F'
                if customer.type == 'adult':
                    type = 'Adult'
                else:
                    type = 'Child'
                cus_res = {
                    'cus_name': customer.partner_id.name,
                    'gender': gender,
                    'type': type,
                    'age': customer.name,
                    'seq': seq,
                    'room': customer.room_no,
                }
                res.append(cus_res)
                seq += 1
            final_res = {
                'from_destination_id': booking.from_destination_id.name,
                'to_destination_id': booking.to_destination_id.name,
                'transport_type_id': booking.transport_type_id.name,
                'transport_carrier_id': booking.transport_carrier_id.name,
                'carrier_id': booking.carrier_id,
                'travel_class_id': booking.travel_class_id.name,
                'pnr': booking.pnr_no,
                'checkin': booking.arrival_date,
                'checkout': booking.depart_date,
                'booking': res
            }
            result_acc.append(final_res)
        return result_acc

    #     def get_transport_information(self,cr,uid,ids,object):
    #         print(object,"object=========get_transport_information===hi",object)
    #         booking_search = self.pool.get('transport.book').search(cr, uid, [('tour_book_id', '=', object.id)])
    #         booking_id = self.pool.get('transport.book').browse(cr,uid, booking_search)
    #         final_res = {}
    #         result_acc = []
    #         cus_res = {}
    #         for booking in booking_id:
    #             print('**********Booking',booking)
    #             address = ''
    #             res = []
    #             seq = 1
    #             for customer in booking.customer_line_ids:
    #                 print('customer............',customer)
    #                 print(customer,"customer")
    #                 if customer.gender == 'male':
    #                     gender = 'M'
    #                 else:
    #                     gender = 'F'
    #                 if customer.type == 'adult':
    #                     type = 'Adult'
    #                 else:
    #                     type = 'Child'
    #                 cus_res = {
    #                             'cus_name' : customer.partner_id.name,
    #                             'gender' : gender,
    #                             'type':type,
    #                             'age':customer.name,
    #                             'seq':seq,
    #                             'room':customer.room_no,
    #                              }
    #                 res.append(cus_res)
    #                 seq += 1
    #             final_res = {
    #                           'from_destination_id' : booking.from_destination_id.name,
    #                           'to_destination_id' : booking.to_destination_id.name,
    #                           'transport_type_id' : booking.transport_type_id.name,
    #                           'transport_carrier_id' : booking.transport_carrier_id.name,
    #                           'carrier_id' : booking.carrier_id,
    #                           'travel_class_id' : booking.travel_class_id.name,
    #                           'pnr' : booking.pnr_no,
    #                           'checkin':booking.arrival_date,
    #                           'checkout':booking.depart_date,
    #                           'booking' : res
    #                               }
    #             result_acc.append(final_res)
    #             print('********Retuning..',final_res)
    #         print('Finally........\n',result_acc)
    #         return result_acc

    def get_partner_lang_date(self, date1, lang):
        record = self.env['res.lang'].search([('code', '=', lang)])
        if len(date1) > 11:
            print('Time')
            new_date = datetime.strftime(datetime.strptime(date1, '%Y-%m-%d %H:%M:%S'), record.date_format)
        else:
            print('Date only')
            new_date = datetime.strftime(datetime.strptime(date1, '%Y-%m-%d'), record.date_format)
        return new_date


#     def get_partner_lang_date(self, cr, uid, ids, date1,lang):     
#         print('******In  get_partner_lang_date')  
#         search_id = self.pool.get('res.lang').search(cr,uid,[('code','=',lang)])
#         record=self.pool.get('res.lang').browse(cr,uid,search_id)
#         if len(date1) > 11:
#             print('Time')
#             new_date=datetime.strftime(datetime.strptime(date1,'%Y-%m-%d %H:%M:%S'),record.date_format)
#         else:
#             print('Date only')
#             new_date=datetime.strftime(datetime.strptime(date1,'%Y-%m-%d'),record.date_format)
#         print("!!!!!!!!!!!!!!!!---new date=",new_date)        
#         return new_date


class tour_booking2(models.Model):
    _inherit = ['tour.booking']

    _description = "Tour Booking"

    def get_partner_lang_date(self, date1, lang):
        record = self.env['res.lang'].search([('code', '=', lang)])
        new_date = datetime.strftime(date1, record.date_format)
        return new_date

    #     def get_partner_lang_date(self, cr, uid, ids, date1,lang):
    #         search_id = self.pool.get('res.lang').search(cr,uid,[('code','=',lang)])
    #         record=self.pool.get('res.lang').browse(cr,uid,search_id)
    #         new_date=datetime.strftime(datetime.strptime(date1,'%Y-%m-%d'),record.date_format)
    # #         print"!!!!!!!!!!!!!!!!---new date=",new_date
    #         return new_date

    def get_hotel_information(self, object):
        booking_id = self.env['tour.hotel.reservation'].search([('tour_book_id', '=', object.id)])
        final_res = {}
        result_acc = []
        cus_res = {}
        for booking in booking_id:
            address = ''
            res = []
            seq = 1
            for customer in booking.tour_customer_ids:
                print(customer, "customer")
                if customer.gender == 'male':
                    gender = 'M'
                else:
                    gender = 'F'
                if customer.type == 'adult':
                    type = 'Adult'
                else:
                    type = 'Child'
                cus_res = {
                    'cus_name': customer.partner_id.name,
                    'gender': gender,
                    'type': type,
                    'age': customer.name,
                    'seq': seq,
                    'room': customer.room_no,
                }
                res.append(cus_res)
                seq += 1

            final_res = {
                'destination_id': booking.destination_id.name,
                'hotel': booking.hotel_id.name,
                'checkin': booking.checkin_date,
                'checkout': booking.checkout_date,
                'booking': res
            }
            result_acc.append(final_res)
        return result_acc

    #     def get_hotel_information(self,cr,uid,ids,object):
    #         print(object,"object==========uuuuuuuuuuuuuuuuuuuuu===get_hotel_information",object,object.id)
    #         booking_search = self.pool.get('tour.hotel.reservation').search(cr,uid, [('tour_book_id', '=', object.id)])
    #         booking_id = self.pool.get('tour.hotel.reservation').browse(cr,uid, booking_search)
    #         print("DDDDDDDDDDDDDDDDDD booking iddd--------",booking_id)
    #         final_res = {}
    #         result_acc = []
    #         cus_res = {}
    #         for booking in booking_id:
    #             address = ''
    #             res = []
    #             seq = 1
    #             for customer in booking.tour_customer_ids:
    #                 print(customer,"customer")
    #                 if customer.gender == 'male':
    #                     gender = 'M'
    #                 else:
    #                     gender = 'F'
    #                 if customer.type == 'adult':
    #                     type = 'Adult'
    #                 else:
    #                     type = 'Child'
    #                 cus_res = {
    #                             'cus_name' : customer.partner_id.name,
    #                             'gender' : gender,
    #                             'type':type,
    #                             'age':customer.name,
    #                             'seq':seq,
    #                             'room':customer.room_no,
    #                              }
    #                 res.append(cus_res)
    #                 seq += 1
    #
    #             final_res = {
    #                           'destination_id' : booking.destination_id.name,
    #                           'hotel' : booking.hotel_id.name,
    #                           'checkin':booking.checkin_date,
    #                           'checkout':booking.checkout_date,
    #                           'booking' : res
    #                               }
    #             result_acc.append(final_res)
    #             print("RESULT========",result_acc)
    #         return result_acc

    def get_end_date(self, object, lang):
        tour_browse = self.env['tour.package'].browse(object.tour_id.id)
        days_to_add = tour_browse.days
        days_to_add = int(days_to_add)
        start_date = object.tour_dates_id.start_date
        st_from = start_date
        end_date = st_from + timedelta(days=days_to_add)
        end_date = str(end_date)[0:10]
        record = self.env['res.lang'].search([('code', '=', lang)])
        new_date = datetime.strftime(datetime.strptime(end_date, '%Y-%m-%d'), record.date_format)
        return new_date

    #     def get_end_date(self,cr,uid,ids,object,lang):
    #         tour_browse = self.pool.get('tour.package').browse(cr,uid, object.tour_id.id)
    #         days_to_add = tour_browse.days
    #         days_to_add = int(days_to_add)
    #         start_date = object.tour_dates_id.start_date
    #         st_from = mx.DateTime.strptime(start_date, '%Y-%m-%d')
    #         end_date = st_from + timedelta(days=days_to_add)
    #         end_date = str(end_date)[0:10]
    #         search_id = self.pool.get('res.lang').search(cr,uid,[('code','=',lang)])
    #         record=self.pool.get('res.lang').browse(cr,uid,search_id)
    #         new_date=datetime.strftime(datetime.strptime(end_date,'%Y-%m-%d'),record.date_format)
    #         return new_date

    @api.model
    def create(self, vals):
        # function overwrites create method and auto generate request no.
        req_no = self.env['ir.sequence'].get('tour.booking')
        print("\n\n\n*****************************",req_no)
        vals['name'] = req_no
        address_browse = self.env['res.partner'].browse(vals['customer_id'])
        if (not address_browse.email) and 'email_id' in vals and vals['email_id']:
            address_browse.write({'email': vals['email_id']})
        if (not address_browse.mobile) and 'mobile1' in vals and vals['mobile1']:
            address_browse.write({'mobile': vals['mobile1']})
        return super(tour_booking2, self).create(vals)

    #     def create(self, cr, uid, vals, context=None):
    #         # function overwrites create method and auto generate request no.
    #         req_no = self.pool.get('ir.sequence').get(cr, uid, 'tour.booking'),
    #         vals['name'] = req_no[0]
    #         address_browse = self.pool.get('res.partner').browse(cr, uid, vals['customer_id'])
    #         print(address_browse, "address_browse")
    #         if (not address_browse.email) and 'email_id' in vals and vals['email_id']:
    #             self.pool.get('res.partner').write(cr, uid, vals['customer_id'], {'email':vals['email_id']})
    #         if (not address_browse.mobile) and 'mobile1' in vals and vals['mobile1']:
    #             self.pool.get('res.partner').write(cr, uid, vals['customer_id'], {'mobile':vals['mobile1']})
    #         return super(tour_booking, self).create(cr, uid, vals, context=context)

    def _get_total_amt(self):
        res = {}
        obj = self[0]
        adult_tour_cost = 0.00
        child_tour_cost = 0.00
        if obj.tour_id:
            for tour_line in obj.tour_id.tour_date_lines:
                if tour_line.id == obj.tour_dates_id.id:
                    adult_tour_cost = get_price(self, obj.pricelist_id.id, tour_line.adult_cost_price)
                    child_tour_cost = get_price(self, obj.pricelist_id.id, tour_line.child_cost_price)
        adult_person = obj.adult
        child_person = obj.child
        tour_cost = (adult_person * adult_tour_cost) + (child_person * child_tour_cost)
        ins_amt = 0.00
        ins_total = 0.00
        for line in obj.insurance_line_ids:
            ins_total = line._get_insurance_cost()
            ins_amt = ins_amt + ins_total[line.id]
        total = tour_cost + ins_amt
        res[obj.id] = total
        return res

    #     def _get_total_amt(self, cr, uid, ids, args1, args2, context=None):
    #         res = {}
    #         total = 0
    #         obj = self.browse(cr, uid, ids)[0]
    #         adult_tour_cost = 0.00
    #         child_tour_cost = 0.00
    #         if obj.tour_id:
    #             for tour_line in obj.tour_id.tour_date_lines:
    #                 if tour_line.id == obj.tour_dates_id.id:
    #                     adult_tour_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, tour_line.adult_cost_price)
    #                     child_tour_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, tour_line.child_cost_price)
    #         adult_person = obj.adult
    #         child_person = obj.child
    #         tour_cost = (adult_person * adult_tour_cost) + (child_person * child_tour_cost)
    #         ins_amt = 0.00
    #         ins_total = 0.00
    #         for line in obj.insurance_line_ids:
    #             ins_total = self.pool.get('tour.insurance.line')._get_insurance_cost(cr, uid, [line.id], args1, args2, context=None)
    #             ins_amt = ins_amt + ins_total[line.id]
    #         total = tour_cost + ins_amt
    #         res[obj.id] = total
    #         return res

    def _get_tour_cost(self):
        res = {}
        total = 0
        for obj in self:
            adult_tour_cost = 0.00
            child_tour_cost = 0.00
            for tour_line in obj.tour_id.tour_date_lines:
                if tour_line.id == obj.tour_dates_id.id:
                    adult_tour_cost = get_price(self, obj.pricelist_id.id, tour_line.adult_cost_price)
                    child_tour_cost = get_price(self, obj.pricelist_id.id, tour_line.child_cost_price)
            adult_person = obj.adult
            child_person = obj.child
            tour_cost = (adult_person * adult_tour_cost) + (child_person * child_tour_cost)
            total = tour_cost
            res[obj.id] = total

        return res

    #     def _get_tour_cost(self, cr, uid, ids, args1, args2, context=None):
    #         res = {}
    #         total = 0
    #         person = 0
    #         for obj in self.browse(cr, uid, ids):
    #             adult_tour_cost = 0.00
    #             child_tour_cost = 0.00
    #             for tour_line in obj.tour_id.tour_date_lines:
    #                 if tour_line.id == obj.tour_dates_id.id:
    #                     adult_tour_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, tour_line.adult_cost_price)
    #                     child_tour_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, tour_line.child_cost_price)
    #             adult_person = obj.adult
    #             child_person = obj.child
    #             tour_cost = (adult_person * adult_tour_cost) + (child_person * child_tour_cost)
    #             total = tour_cost
    #             res[obj.id] = total
    #
    #         return res

    def _get_transport_cost(self):
        res = {}
        total = 0
        res[self.id] = total
        return res

    #     def _get_transport_cost(self, cr, uid, ids, args1, args2, context=None):
    #         res = {}
    #         total = 0
    #         tot_person = 0
    #         obj = self.browse(cr, uid, ids)[0]
    #         res[obj.id] = total
    #         return res

    def _get_insurance_total_amt(self):
        res = {}
        total = 0
        for obj in self:
            for line in obj.insurance_line_ids:
                ins_total = line._get_insurance_cost()
                total = total + ins_total[line.id]
                res[obj.id] = total
        res[obj.id] = total
        return res

    #     def _get_insurance_total_amt(self, cr, uid, ids, args1, args2, context=None):
    #         res = {}
    #         total = 0
    #         for obj in self.browse(cr, uid, ids):
    #             for line in obj.insurance_line_ids:
    #                 ins_total = self.pool.get('tour.insurance.line')._get_insurance_cost(cr, uid, [line.id], args1, args2, context=None)
    #                 total = total + ins_total[line.id]
    #                 res[obj.id] = total
    #         res[obj.id] = total
    #         return res

    @api.one
    def _amount_all(self):
        res = {}
        taxes = []
        if self._context is None:
            self._context = {}
        obj = self
        adult_tour_cost = 0.00
        child_tour_cost = 0.00
        if obj.tour_id:
            for tour_line in obj.tour_id.tour_date_lines:
                if tour_line.id == obj.tour_dates_id.id:
                    adult_tour_cost = get_price(self, obj.pricelist_id.id, tour_line.adult_cost_price)
                    child_tour_cost = get_price(self, obj.pricelist_id.id, tour_line.child_cost_price)
        adult_person = obj.adult
        child_person = obj.child
        tour_cost = (adult_person * adult_tour_cost) + (child_person * child_tour_cost)
        ins_amt = 0.00
        ins_total = 0.00
        tour_tax = 0.00
        insu_tax = 0.00
        tour_taxs = obj.tour_id.product_id.taxes_id.compute_all(tour_cost, None, 1, obj.tour_id.product_id)
        if tour_taxs['taxes']:
            for tax in tour_taxs['taxes']:
                tour_tax = tour_tax + tax['amount']

        for line in obj.insurance_line_ids:
            ins_total = line._get_insurance_cost()
            ins_amt = ins_amt + ins_total[line.id]
            prod = self.env['product.product'].search([('name', '=', 'Insurance')])
            if prod:
                prod_brw = prod[0]
                insu_taxs = prod_brw.taxes_id.compute_all(ins_amt, None, 1, prod_brw.id)
                if insu_taxs['taxes']:
                    for tax in insu_taxs['taxes']:
                        insu_tax = insu_tax + tax['amount']
        total = tour_cost + ins_amt
        sub_total = 0.0
        tot_with_tax = 0.0
        total_tax = 0.0
        records = self
        price = 0
        for line in records[0].product_line_ids:
            price = line.price_unit
            taxes = line.tax_id.compute_all(price, None, line.qty, line.product_id)
            sub_total = sub_total + taxes['total_excluded']
            tot_with_tax = tot_with_tax + taxes['total_included']
            if taxes['taxes']:
                for tax in taxes['taxes']:
                    total_tax = total_tax + tax['amount']
        res[records[0].id] = {
            'subtotal': 0.0,
            'total_amt': 0.0,
            'tax_amt': 0.0,
        }
        res[records[0].id]["subtotal"] = total + price
        res[records[0].id]["total_amt"] = total + price + tour_tax + insu_tax + total_tax
        if taxes or insu_tax or tour_taxs:
            res[records[0].id]["tax_amt"] = tour_tax + insu_tax + total_tax
        # return res

    #     def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
    #
    #         res = {}
    #         if context is None:
    #             context = {}
    #         sub_total = 0.0
    #         tot_with_tax = 0.0
    #         total_tax = 0.0
    #         taxes = {}
    #         records = self.browse(cr, uid, ids, context=context)
    #         for line in records[0].product_line_ids:
    #             price = line.price_unit
    #             taxes = line.tax_id.compute_all(price, None, line.qty, line.product_id)
    #
    #
    #             """
    #                 The tax_obj.compute_all method returns the following dictionary..........
    #         RETURN: {
    #                     'total': 0.0,                # Total without taxes
    #                     'total_included: 0.0,        # Total with taxes
    #                     'taxes': []                  # List of taxes, see compute for the format
    #                 }
    #         """
    #             sub_total = sub_total + taxes['total_included']
    #             tot_with_tax = tot_with_tax + taxes['total_excluded']
    #             if taxes['taxes']:
    #                 for  tax in taxes['taxes']:
    #                     total_tax = total_tax + tax['amount']
    #
    #
    #
    #         res[records[0].id] = {
    #                 'subtotal': 0.0,
    #                 'total_amt': 0.0,
    #                 'tax_amt': 0.0,
    #             }
    #
    #         res[records[0].id]["subtotal"] = tot_with_tax
    #         res[records[0].id]["total_amt"] = sub_total + records[0].total_insurance_amt
    #         res[records[0].id]["tax_amt"] = sub_total - tot_with_tax
    #         return res

    def _get_order(self):
        result = {}
        for line in self.env['tour.package.products.line'].browse(self._ids):
            result[line.tour_package_id.id] = True
        return list(result.keys())

    #     def _get_order(self, cr, uid, ids, context=None):
    #         print("get order")
    #         result = {}
    #         for line in self.pool.get('tour.package.products.line').browse(cr, uid, ids, context=context):
    #             result[line.tour_package_id.id] = True
    #         return list(result.keys())

    name = fields.Char("Tour Booking ID", size=50, readonly=True)

    current_date = fields.Date("Booking Date", required=True, readonly=True, states={'draft': [('readonly', False)]},
                               default=lambda *args: time.strftime('%Y-%m-%d'))
    customer_id = fields.Many2one('res.partner', 'Customer', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]})
    email_id = fields.Char('Email Id', size=150, readonly=True, states={'draft': [('readonly', False)]})
    mobile1 = fields.Char('Mobile Number', size=200, required=True, readonly=True,
                          states={'draft': [('readonly', False)]})
    adult = fields.Integer("Adult Persons", readonly=True, states={'draft': [('readonly', False)]})
    child = fields.Integer("Child", readonly=True, states={'draft': [('readonly', False)]})
    tour_type = fields.Selection([
        ('international', 'International'),
        ('domestic', 'Domestic'),
    ], "Tour Type", required=True, readonly=True, states={'draft': [('readonly', False)]})
    via = fields.Selection([
        ('direct', 'Direct'),
        ('agent', 'Agent'),
    ], "Via", required=True, readonly=True, states={'draft': [('readonly', False)]}, default=lambda *a: 'direct')
    season_id = fields.Many2one('tour.season', 'Season', required=True, readonly=True,
                                states={'draft': [('readonly', False)]})
    agent_id = fields.Many2one('res.partner', 'Agent', readonly=True, states={'draft': [('readonly', False)]})
    tour_id = fields.Many2one('tour.package', "Tour", required=True, readonly=True,
                              states={'draft': [('readonly', False)]})
    tour_dates_id = fields.Many2one('tour.dates', string="Tour Dates", required=False, readonly=False)
    payment_policy_id = fields.Many2one('tour.payment.policy', "Payment Policy", required=True, readonly=True,
                                        states={'draft': [('readonly', False)]})
    adult_coverage = fields.Integer("Number of Adult Persons Policy Coverage", readonly=True,
                                    states={'draft': [('readonly', False)]})
    child_coverage1 = fields.Integer("Number of Child Policy Coverage", readonly=True,
                                     states={'draft': [('readonly', False)]})
    total_insurance_amt = fields.Float(compute=_get_insurance_total_amt, string="Insurance Amount", store=True,
                                       readonly=True, states={'draft': [('readonly', False)]})
    insurance_line_ids = fields.One2many('tour.insurance.line', 'tour_book_id', 'Insurance Line', readonly=True,
                                         states={'draft': [('readonly', False)]})
    tour_customer_ids = fields.One2many('tour.customer.details', 'tour_book_id', 'Tour Customer Details', readonly=True,
                                        states={'draft': [('readonly', False)]})
    tour_booking_invoice_ids = fields.Many2many('account.invoice', 'tour_booking_invoice_rel', 'tour_booking_id',
                                                'invoice_id', 'Tour Invoices', readonly=True,
                                                states={'draft': [('readonly', False)]})
    tour_sale_order_ids = fields.Many2many('sale.order', 'tour_sale_order_rel', 'tour_book_id', 'sale_order_id',
                                           'Sales Orders', readonly=True, states={'draft': [('readonly', False)]})
    tour_cost = fields.Float(compute=_get_tour_cost, string="Tour Cost", store=True, readonly=True,
                             states={'draft': [('readonly', False)]})
    transport_cost = fields.Float(compute=_get_transport_cost, string="Transport Cost", store=True, readonly=True,
                                  states={'draft': [('readonly', False)]})
    # total_amt = fields.Float(compute=_get_total_amt, string="Total Amount", store=True, readonly=True, states={'draft': [('readonly', False)]})
    commission_compute = fields.Boolean('Commission computed', readonly=True, states={'draft': [('readonly', False)]})
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', readonly=True,
                                   states={'draft': [('readonly', False)]})
    product_line_ids = fields.One2many('tour.package.products.line', 'tour_booking_id', 'Product')
    subtotal = fields.Float(compute='calculate_tax', string='Subtotal', multi='sums', help="Subtotal", store=True)
    tax_amt = fields.Float(compute='calculate_tax', string='Total Taxed Amount', multi='sums',
                           help="Total Taxed Amount", store=True)
    total_amt = fields.Float(compute='calculate_tax', string='Total Amount', multi='sums',
                             help="Total Amount Including Tax", store=True)
    # subtotal = fields.Float(related='tour_sale_order_ids.amount_total', string='Subtotal',multi='sums', help="Subtotal")
    sale_order_count = fields.Integer(compute='_compute_sale_order_count', string='Sale Order Count')


    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('in_process', 'In Process'),
        ('booked', 'Booked'),
        ('invoiced', 'Invoiced'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ], 'Status', readonly=True, states={'draft': [('readonly', False)]}, default=lambda *a: 'draft')

    #     def on_change_tour_id(self,cr,uid,ids,tour_id):
    #         result = {}
    #         if tour_id:
    #             obj = self.pool.get('tour.package').browse(cr,uid,tour_id)
    #             print "obj================================obj.product_line_id=============",obj.product_line_id
    #             result['product_line_ids'] = obj.product_line_id
    #             print "resultresultresult======================+++++++++++++============================",result
    #           #  result['mobile1'] = obj.mobile
    #         return {'value': result}
    #

    #     def on_change_customer_id(self, cr, uid, ids, customer_id):
    #         result = {}
    #         if customer_id:
    #             obj = self.pool.get('res.partner').browse(cr, uid, customer_id)
    #             result['email_id'] = obj.email
    #             result['mobile1'] = obj.mobile
    #         return {'value': result}


    @api.multi
    def call_so_from_booking(self):
        res = self.env['sale.order'].search([('tour_book_id', '=', self.id)])

        # type: 'ir.actions.act_window',
        # res_model: 'mod.flight',
        # view_mode: 'form',
        # view_type: 'form',
        # views: [[false, 'form']],
        # target: 'current',
        # res_id: result
        #
        # return {
        #     'name':'Sale Order',
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     'view_type': 'tree',
        #     'views': [False, 'list'],
        #     # 'domain': [('tour_book_id','in',res.ids)]
        # }
        if res:
            return {
                    'name'      : _('Sale Order'),
                    'type'      : 'ir.actions.act_window',
                    'res_model' : 'sale.order',
                    'view_type' : 'tree',
                    'view_mode' : 'tree,form',
                    'res_id'    : res[0].id,
                    'domain': [('tour_book_id','in',res.ids)]
                }


    def _compute_sale_order_count(self):
        sale_data = self.env['sale.order'].read_group(domain=[('partner_id', 'child_of', self.ids)],
                                                      fields=['partner_id'], groupby=['partner_id'])
        # read to keep the child/parent relation while aggregating the read_group result in the loop
        self.sale_order_count=len(self.env['sale.order'].search([('tour_book_id','=',self.id)]))
        # self.sale_order_count=self.customer_id.sale_order_count
    @api.multi
    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        result = {}
        if self.customer_id:
            result['email_id'] = self.customer_id.email
            result['mobile1'] = self.customer_id.mobile
            result['pricelist_id'] = self.customer_id.property_product_pricelist
        return {'value': result}

    @api.multi
    @api.depends('state', 'tour_sale_order_ids')
    def calculate_tax(self):
        if self.state == "in_process":
            subtot = 0
            tax_amt = 0
            tot_amt = 0
            for rec in self.tour_sale_order_ids:
                subtot += rec.amount_untaxed
                tax_amt += rec.amount_tax
                tot_amt += rec.amount_total
            print(tot_amt)
            self.subtotal = subtot
            self.tax_amt = tax_amt
            self.total_amt = tot_amt

        if self.state == "invoiced":
            subtot = 0
            tax_amt = 0
            tot_amt = 0
            for rec in self.tour_sale_order_ids:
                subtot += rec.amount_untaxed
                tax_amt += rec.amount_tax
                tot_amt += rec.amount_total
            print(tot_amt)
            self.subtotal = subtot
            self.tax_amt = tax_amt
            self.total_amt = tot_amt

        if self.state == "done":
            subtot = 0
            tax_amt = 0
            tot_amt = 0
            for rec in self.tour_sale_order_ids:
                subtot += rec.amount_untaxed
                tax_amt += rec.amount_tax
                tot_amt += rec.amount_total
            print(tot_amt)
            self.subtotal = subtot
            self.tax_amt = tax_amt
            self.total_amt = tot_amt

    @api.depends('tour_type')
    @api.onchange('season_id', 'tour_type')
    def onchange_season_id(self):
        self.tour_id = None
        if self.season_id and not self.tour_type:
            raise Warning("Please select Tour Type")
        elif self.season_id:
            tour_package_ids = self.env['tour.package'].search([('tour_type', '=', self.tour_type)])
            print(tour_package_ids)
            tour_ids_with_same_season = []
            for tour in tour_package_ids:
                print(tour)
                [tour_ids_with_same_season.append(line.tour_id.id) for line in tour.tour_date_lines if
                 line.season_id.id == self.season_id.id]
            print(tour_ids_with_same_season)
            return {
                'domain': {
                    'tour_id': [('id', 'in', tour_ids_with_same_season)]
                }
            }

    @api.onchange('tour_id')
    def onchange_tour_id(self):
        self.tour_dates_id = None
        tour_ids_with_same_season = []
        # print ("------------------------------------------------In onchange22222")
        if self.tour_id and not self.season_id:
            raise Warning("Please select Season first")

        elif self.tour_id:
            [tour_ids_with_same_season.append(line.tour_id.id) for line in self.tour_id.tour_date_lines if
             line.season_id.id == self.season_id.id]

            # print (self.season_id)
            # for line in self.tour_id.tour_date_lines:
            # print (line)
            # print (line.season_id.id)
            # print (line.season_id)
            # if line.season_id.id==self.season_id.id:
            # [tour_ids_with_same_season.append(line.tour_id.id)]

            return {
                'domain': {
                    'tour_dates_id.season_id': [('id', 'in', tour_ids_with_same_season)]
                }
            }

    @api.onchange('tour_dates_id')
    def onchange_tour_date(self):
        if self.tour_dates_id and not self.tour_id:
            raise Warning("Please select Tour first")

    #         result = {}
    #         res1 = []
    #         lst = []
    #         if self.season_id and self.tour_id and self.current_date:
    #             for o in self.tour_id.product_line_id:
    #                 lst.append (o.id)
    #             result['product_line_ids'] = lst
    #             for line in self.tour_id.tour_date_lines:
    #                 if line.season_id.id == self.season_id and line.book_date >= self.current_date and line.state == 'available':
    #                     res1.append(line.id)
    #         res2 = {
    #                'domain': {
    #                 'tour_dates_id': [('id', 'in', res1)],
    #            } , 'value': result}
    #         return res2

    #     def onchange_tour_id(self, cr, uid, ids, tour_id, season_id, current_date):
    #         result = {}
    #         res2 = {}
    #         res1 = []
    #         lst = []
    #         if season_id and tour_id and current_date:
    #             obj = self.pool.get('tour.package').browse(cr, uid, tour_id)
    #             for o in obj.product_line_id:
    #                 lst.append (o.id)
    #             result['product_line_ids'] = lst
    #             for line in obj.tour_date_lines:
    #                 print(line, "line")
    #                 if line.season_id.id == season_id and line.book_date >= current_date and line.state == 'available':
    #                     res1.append(line.id)
    #         res2 = {
    #                'domain': {
    #                 'tour_dates_id': [('id', 'in', res1)],
    #            } , 'value': result}
    #         print(res1, "res1")
    #         return res2

    #     _defaults = {
    #                  'state': lambda * a: 'draft',
    #                  'via': lambda * a: 'direct',
    #                  'current_date':lambda *args: time.strftime('%Y-%m-%d'),
    #
    #                  }

    @api.multi
    def tour_cancel(self):
        self.write({'state': 'cancel'})
        return True

    #     def tour_cancel(self, cr, uid, ids, *args):
    #         self.write(cr, uid, ids, {'state':'cancel'})
    #         return True

    def check_availability(self):
        tot_person = 0
        for obj in self:
            print
            if not obj.pricelist_id:
                raise UserError('Pricelist is not define')
            if obj.adult + obj.child == 0:
                raise UserError(' Please Enter number of  Adults and Child ')
            if not obj.tour_customer_ids:
                raise UserError('Customer details is not define')
            adult_len = 0
            child_len = 0
            for customer in obj.tour_customer_ids:
                if customer.type == 'adult':
                    adult_len += 1
                else:
                    child_len += 1
            if not (adult_len == obj.adult and child_len == obj.child):
                raise UserError('Customer Details is not proper')
            tot_person = len(obj.tour_customer_ids)
            obj.tour_dates_id
            if tot_person > obj.tour_dates_id.available_seat:
                raise UserError('NO SEATS ARE AVAILABLE,  TOUR IS ALREADY BOOKED')
            if obj.tour_dates_id.season_id.id == obj.season_id.id and obj.tour_dates_id.state != 'available':
                raise UserError('TOUR IS NOT AVAILABLE FOR THIS SEASON')
            date=time.strftime('%Y-%m-%d')
            date=datetime.strptime(date,'%Y-%m-%d').date()
            if not (obj.tour_dates_id.book_date >= date):
#                 datetime.strptime(date_str, '%m-%d-%Y').date()
                raise UserError('Tour Booking Is Closed')
            visa = False
            for visa_line in obj.tour_id.tour_destination_lines:
                if visa_line.is_visa == True:
                    visa = True
                    break
            if visa == True:
                for customer in obj.tour_customer_ids:
                    customer.write({'v_flag': True})
            self.write({'state': 'confirm'})    #                raise osv.except_osv(_('Error !'), _('Tour Booking Is Closed'))

        return True

    #     def check_availability(self, cr, uid, ids, *args):
    #         tot_person = 0
    #         for obj in self.browse(cr, uid, ids):
    #            if not obj.pricelist_id:
    #                raise osv.except_osv(_('Error !'), _('Pricelist is not define'))
    #            if obj.adult + obj.child == 0:
    #                raise osv.except_osv(_('Error !'), _(' Please Enter number of  Adults and Child '))
    #            if not obj.tour_customer_ids:
    #                raise osv.except_osv(_('Error !'), _('Customer details is not define'))
    #            adult_len = 0
    #            child_len = 0
    #            for customer in obj.tour_customer_ids:
    #                if customer.type == 'adult':
    #                    adult_len += 1
    #                else:
    #                    childvals.get_len += 1
    #            print(adult_len, "adult_len", child_len, "child_len")
    #            print(obj.adult, "adult_obj", obj.child, "child_obj")
    #            if not (adult_len == obj.adult and child_len == obj.child):
    #                raise osv.except_osv(_('Error !'), _('Customer Details is not proper'))
    #            tot_person = len(obj.tour_customer_ids)
    #            obj.tour_dates_id
    #            if tot_person > obj.tour_dates_id.available_seat:
    #                raise osv.except_osv(_('Error !'), _('NO SEATS ARE AVAILABLE,  TOUR IS ALREADY BOOKED'))
    #            if obj.tour_dates_id.season_id.id == obj.season_id.id and obj.tour_dates_id.state != 'available':
    #                raise osv.except_osv(_('Error !'), _('TOUR IS NOT AVAILABLE FOR THIS SEASON'))
    #            if not (obj.tour_dates_id.book_date >= time.strftime('%Y-%m-%d')):
    #                raise osv.except_osv(_('Error !'), _('Tour Booking Is Closed'))
    #            visa = False
    #            for visa_line in obj.tour_id.tour_destination_lines:
    #                if visa_line.is_visa == True:
    #                    visa = True
    #                    break
    #            if visa == True:
    #                for customer in obj.tour_customer_ids:
    #                    self.pool.get('tour.customer.details').write(cr, uid, customer.id, {'v_flag':True})
    #            self.write(cr, uid, ids, {'state':'confirm'})
    #            return True

    def create_order(self):
        txlst = []
        obj = self[0]
        pricelist_id = obj.pricelist_id.id
        a = obj.tour_id.product_id.product_tmpl_id.property_account_income_id.id
        if not a:
            a = obj.tour_id.product_id.categ_id.property_account_income_categ_id.id
        if not a:
            raise UserError('There is no income account defined ' \
                            'for this product: "%s" (id:%d)' % \
                            obj.tour_id.product_id.name, obj.tour_id.product_id.id)

        sale_id = self.env['sale.order'].create({
            'picking_policy': 'one',
            'order_policy': 'prepaid',
            'invoice_quantity': 'Ordered Quantities',
            'origin': obj.name,
            'partner_id': obj.customer_id.id,
            'partner_invoice_id': obj.customer_id.id,
            'partner_order_id': obj.customer_id.id,
            'partner_shipping_id': obj.customer_id.id,
            'pricelist_id': pricelist_id,
            'invoiced_amt': 0.0,
            'tour_book_id': obj.id,
            'tour_id': obj.tour_id.id,
        })
        txlst1 = []
        txlst2 = []
        adult_tour_cost = 0.00
        child_tour_cost = 0.00
        if obj.tour_id:
            for tour_line in obj.tour_id.tour_date_lines:
                if tour_line.id == obj.tour_dates_id.id:
                    adult_tour_cost = get_price(self, obj.pricelist_id.id, tour_line.adult_cost_price)
                    
                    child_tour_cost = get_price(self, obj.pricelist_id.id, tour_line.child_cost_price)
            adult_person = obj.adult
            child_person = obj.child
            tour_cost = (adult_person * adult_tour_cost) + (child_person * child_tour_cost)
            for tx in obj.tour_id.product_id.taxes_id:
                if tx.id not in txlst1:
                    txlst1.append(tx.id)
            line_data1 = {
                'name': obj.tour_id.product_id.name,
                'product_uom_qty': 1,
                'product_id': obj.tour_id.product_id.id,
                'account_id': a,
                'product_uom': 1,
                'price_unit': tour_cost,
                'order_id': sale_id.id,
                'tax_id': [(6, 0, txlst1)]
            }
            line_obj1 = self.env['sale.order.line'].create(line_data1)

        for line in obj.product_line_ids:
            for tx in line.tax_id:
                if tx.id not in txlst:
                    txlst.append(tx.id)
            line_data = {
                'name': line.name,
                'product_uom_qty': line.qty,
                'product_id': line.product_id.id,
                'account_id': a,
                'product_uom': 1,
                'price_unit': line.price_unit,
                'order_id': sale_id.id,
                'tax_id': [(6, 0, txlst)]
            }
            print("line_data", line_data)
            line_obj = self.env['sale.order.line'].create(line_data)
            txlst = []

        if obj.insurance_line_ids:
            prod = self.env['product.product'].search([('name', '=', 'Insurance')])
            if prod:
                prod_brw = prod[0]
                acc_id = prod_brw.property_account_income_id.id
                if not acc_id:
                    acc_id = prod_brw.categ_id.property_account_income_categ_id.id
                if not acc_id:
                    raise UserError('There is no income account defined ' \
                                    'for this product: "%s" (id:%d)' % prod_brw.name, prod_brw.id)
                for tx in prod_brw.taxes_id:
                    if tx.id not in txlst2:
                        txlst2.append(tx.id)
                line_data2 = {
                    'name': prod_brw.name,
                    'product_uom_qty': 1,
                    'product_id': prod_brw.id,
                    'account_id': acc_id,
                    'product_uom': 1,
                    'price_unit': obj.total_insurance_amt,
                    'order_id': sale_id.id,
                    'tax_id': [(6, 0, txlst2)]
                }
                line_obj1 = self.env['sale.order.line'].create(line_data2)
        self._cr.execute('insert into tour_sale_order_rel(tour_book_id,sale_order_id) values (%s,%s)',
                         (obj.id, sale_id.id))
        self._cr.execute('insert into tour_partner_history_rel(tour_booking_id,partner_id) values (%s,%s)',
                         (obj.customer_id.id, obj.id))
        self.write({'state': 'in_process'})
        return True

    #     def create_order(self, cr, uid, ids, *args):
    #         txlst = []
    #         fiscal_position = False
    #         obj = self.browse(cr, uid, ids)[0]
    #         pricelist_id = obj.pricelist_id.id
    #         a = obj.tour_id.product_id.product_tmpl_id.property_account_income_id.id
    #         if not a:
    #             a = obj.tour_id.product_id.categ_id.property_account_income_categ_id.id
    #         if not a:
    #             raise osv.except_osv(_('Error !'),
    #                     _('There is no income account defined ' \
    #                             'for this product: "%s" (id:%d)') % \
    #                             (obj.tour_id.product_id.name, obj.tour_id.product_id.id,))
    #
    #         sale_config_ids = []
    #         sale_config_ids = self.pool.get('sale.config.settings').search(cr, 1, [])
    #         if sale_config_ids:
    #             sale_config_id = max(sale_config_ids)
    #             sale_browse = self.pool.get('sale.config.settings').browse(cr, uid, sale_config_id)
    #         sale_id = self.pool.get('sale.order').create(cr, uid, {
    #                                                                'picking_policy': 'one',
    #                                                                'order_policy':'prepaid',
    #                                                                'invoice_quantity': 'Ordered Quantities',
    #                                                                'origin': obj.name,
    #                                                                'partner_id': obj.customer_id.id,
    #                                                                'partner_invoice_id':obj.customer_id.id,
    #                                                                'partner_order_id':obj.customer_id.id,
    #                                                                'partner_shipping_id':obj.customer_id.id,
    #                                                                'pricelist_id': pricelist_id,
    #                                                                'invoiced_amt': 0.0,
    #                                                                'tour_book_id': obj.id,
    #                                                                'tour_id':obj.tour_id.id,
    #                                                                })
    #         fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
    #         txlst1=[]
    #         txlst2=[]
    #         adult_tour_cost = 0.00
    #         child_tour_cost = 0.00
    #         if obj.tour_id:
    #             for tour_line in obj.tour_id.tour_date_lines:
    #                 if tour_line.id == obj.tour_dates_id.id:
    #                     adult_tour_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, tour_line.adult_cost_price)
    #                     child_tour_cost = get_price(self, cr, uid, ids, obj.pricelist_id.id, tour_line.child_cost_price)
    #             adult_person = obj.adult
    #             child_person = obj.child
    #             tour_cost = (adult_person * adult_tour_cost) + (child_person * child_tour_cost)
    #             for tx in obj.tour_id.product_id.taxes_id:
    #                 if tx.id not in txlst1:
    #                     txlst1.append(tx.id)
    #             line_data1 = {
    #                         'name': obj.tour_id.product_id.name,
    #                         'product_uom_qty': 1,
    #                         'product_id': obj.tour_id.product_id.id,
    #                         'account_id':a,
    #                         'product_uom': 1,
    #                         'price_unit': tour_cost,
    #                         'order_id': sale_id,
    #                         'tax_id':[(6,0,txlst1)]
    #                         }
    #             line_obj1=self.pool.get('sale.order.line').create(cr, uid, line_data1)
    #
    #         for line in obj.product_line_ids:
    #             for tx in line.tax_id:
    #                 if tx.id not in txlst:
    #                     txlst.append(tx.id)
    #             line_data = {
    #                         'name': line.name,
    #                         'product_uom_qty': line.qty,
    #                         'product_id': line.product_id.id,
    #                         'account_id':a,
    #                         'product_uom': 1,
    #                         'price_unit': line.price_unit,
    #                         'order_id': sale_id,
    #                         'tax_id':[(6, 0, txlst)]
    #                         }
    #             print("line_data", line_data)
    #             line_obj = self.pool.get('sale.order.line').create(cr, uid, line_data)
    #             txlst = []
    #
    #         if obj.insurance_line_ids:
    #             prod = self.pool.get('product.product').search(cr,uid,[('name','=','Insurance')])
    #             if prod:
    #                 prod_brw = self.pool.get('product.product').browse(cr,uid,prod)[0]
    #                 acc_id = prod_brw.property_account_income_id.id
    #                 if not acc_id:
    #                     acc_id = prod_brw.categ_id.property_account_income_categ_id.id
    #                 if not acc_id:
    #                     raise osv.except_osv(_('Error !'),
    #                             _('There is no income account defined ' \
    #                                     'for this product: "%s" (id:%d)') % \
    #                                     (prod_brw.name, prod_brw.id,))
    #                 for tx in prod_brw.taxes_id:
    #                     if tx.id not in txlst2:
    #                         txlst2.append(tx.id)
    #                 line_data2 = {
    #                             'name': prod_brw.name,
    #                             'product_uom_qty': 1,
    #                             'product_id': prod_brw.id,
    #                             'account_id':acc_id,
    #                             'product_uom': 1,
    #                             'price_unit': obj.total_insurance_amt,
    #                             'order_id': sale_id,
    #                             'tax_id':[(6,0,txlst2)]
    #                             }
    #                 line_obj1=self.pool.get('sale.order.line').create(cr, uid, line_data2)
    #         cr.execute('insert into tour_sale_order_rel(tour_book_id,sale_order_id) values (%s,%s)', (obj.id, sale_id))
    #         cr.execute('insert into tour_partner_history_rel(tour_booking_id,partner_id) values (%s,%s)', (obj.customer_id.id, obj.id))
    #         self.write(cr, uid, ids, {'state':'in_process'})
    #         return True

    def confirm_booking(self):
        date=time.strftime('%Y-%m-%d')
        date=datetime.strptime(date, '%Y-%m-%d').date()

        tot_person = 0
        for obj in self:
            tot_person = obj.adult + obj.child
            payment_amt = 0.0
            percen = 0.0
            percen = float(obj.payment_policy_id.before_book_date_perc) / 100

            for i in range(0, len(obj.tour_sale_order_ids)):
                if obj.tour_sale_order_ids[i].state == 'draft':
                   raise UserError(' Please Confirm The Sale Order Before Booking')
            seats = 0
            person = 0
            for i in range(0, len(obj.tour_booking_invoice_ids)):
                if obj.tour_booking_invoice_ids[i].state == 'draft':
                    raise UserError(' Please Validate The Invoice Before Booking')
                print(obj.tour_dates_id)
                if obj.tour_dates_id.book_date >= date:
                    payment_amt = obj.tour_booking_invoice_ids[i].amount_total * percen
                    actual_pay = obj.tour_booking_invoice_ids[i].amount_total - payment_amt
                    if obj.tour_booking_invoice_ids[i].residual > actual_pay:
                        raise Warning(' Please Pay The Booking Amount')
                    seats = obj.tour_dates_id.available_seat
                    if seats == 0:
                        raise Warning(' No Seats Available')
                    person = seats - tot_person
                    obj.tour_dates_id.write({'available_seat': person})
                else:

                    raise Warning('Tour Booking Is Closed')

            self._cr.execute('insert into tour_booking_customer_rel(tour_booking_customer_id,tour_id) values (%s,%s)',
                             (obj.tour_id.id, obj.id))
            self._cr.execute("""select id from product_template where name='Passport'""")
            p_id = self._cr.fetchone()
            self._cr.execute("""select id from product_template where name='Visa'""")
            v_id = self._cr.fetchone()
            self._cr.execute("""select id from service_scheme where name='Regular'""")
            s_id = self._cr.fetchone()
            self._cr.execute("""select service_cost from service_scheme where name='Regular'""")
            s_cost = self._cr.fetchone()
            pricelist_id = obj.pricelist_id.id
            for hot_line in obj.tour_id.tour_destination_lines:
                for lines in hot_line.hotel_lines:
                    search_id = self.env['hotel.information'].search(
                        [('hotel_id', '=', lines.hotel_id.id), ('state', '=', 'confirm')], limit=1)
                    if not search_id:
                        raise UserError('hotel information does not exist')
                    if lines.name:
                        room_rent = hotel_rent = 0.00
                        if lines.room_type_id.seller_ids:
                            for line in lines.room_type_id.seller_ids:
                                if line.name.id == lines.hotel_id.id:
                                    room_rent = get_price(self, pricelist_id, line.price)
                                    hotel_rent = get_price(self, pricelist_id, line.sale_price)

                        vals = {
                            'customer_id': obj.customer_id.id,
                            'current_date': obj.current_date,
                            'email_id': obj.email_id,
                            'mobile': obj.mobile1,
                            'adult': obj.adult,
                            'child': obj.child,
                            'hotel_type_id': lines.hotel_type_id.id,
                            'hotel_id': search_id.id,
                            'room_type_id': lines.room_type_id.id,
                            'room_rent': room_rent,
                            'hotel_rent': hotel_rent,
                            'tour_id': obj.tour_id.id,
                            'tour_book_id': obj.id,
                            'tour_start_date': obj.tour_dates_id.id,
                            'destination_id': hot_line.destination_id.id,
                            'pricelist_id': pricelist_id,
                        }
                        hot_id = self.env['tour.hotel.reservation'].create(vals)

                        tax_id = self.env['account.fiscal.position'].map_tax(lines.room_type_id.taxes_id)
                        if tax_id:
                            for txid in tax_id:
                                self._cr.execute(
                                    'insert into hotel_reservation_tax(hotel_res_id,tax_id) values (%s,%s)',
                                    (hot_id.id, txid.id))
                        for customer_line in obj.tour_customer_ids:

                            if customer_line.h_flag == True:
                                cust_vals = {
                                    'name': customer_line.name,
                                    'partner_id': customer_line.partner_id.id,
                                    'type': customer_line.type,
                                    'gender': customer_line.gender,
                                    'hotel_res_id': hot_id.id,
                                }
                                self.env['tour.customer.details'].create(cust_vals)
            transport = False
            for cust_line in obj.tour_customer_ids:
                if cust_line.t_flag == True:
                    transport = True
            if transport:
                for hot_line in obj.tour_id.tour_road_travel_lines:
                    for lines in hot_line.provider_ids:
                        if lines.name:

                            cost_price = 0.00
                            sale_price = 0.00
                            cost_price_child = 0.00
                            sale_price_child = 0.00
                            if lines.provider_id.transport_type_info_ids:
                                for line in lines.provider_id.transport_type_info_ids:
                                    if (
                                            line.from_date <= obj.current_date and obj.current_date <= line.to_date and line.transport_carrier_id.id == lines.transport_carrier_id.id and
                                            line.transport_type_id.id == hot_line.transport_type_id.id and line.travel_class_id.id == hot_line.travel_class_id.id and
                                            line.from_destination_id.id == hot_line.from_destination_id.id and line.to_destination_id.id == hot_line.to_destination_id.id):
                                        cost_price = get_price(self, pricelist_id, line.cost_price)
                                        sale_price = get_price(self, pricelist_id, line.sale_price)
                                        cost_price_child = get_price(self, pricelist_id, line.cost_price_child)
                                        sale_price_child = get_price(self, pricelist_id, line.sale_price_child)
                            vals = {
                                'customer_id': obj.customer_id.id,
                                'current_date': obj.current_date,
                                'email_id': obj.email_id,
                                'mobile': obj.mobile1,
                                'adult': obj.adult,
                                'child': obj.child,
                                'transport_id': lines.provider_id.id,
                                'transport_carrier_id': lines.transport_carrier_id.id,
                                'transport_type_id': hot_line.transport_type_id.id,
                                'travel_class_id': hot_line.travel_class_id.id,
                                'from_destination_id': hot_line.from_destination_id.id,
                                'to_destination_id': hot_line.to_destination_id.id,
                                'tour_id': obj.tour_id.id,
                                'tour_book_id': obj.id,
                                'start_date': obj.tour_dates_id.id,
                                'pricelist_id': pricelist_id,
                                'cost_price': cost_price,
                                'sale_price': sale_price,
                                'cost_price_child': cost_price_child,
                                'sale_price_child': sale_price_child,
                            }
                            print("Transport vals", vals)
                            trans_id = self.env['transport.book'].create(vals)

                            tax_id = self.env['account.fiscal.position'].map_tax(hot_line.transport_type_id.taxes_id)
                            if tax_id:
                                for txid in tax_id:
                                    self._cr.execute(
                                        'insert into transport_book_tax(transport_type_id,tax_id) values (%s,%s)',
                                        (trans_id, txid.id))

                            for customer_line in obj.tour_customer_ids:
                                if customer_line.t_flag == True:
                                    cust_vals = {
                                        'name': customer_line.name,
                                        'partner_id': customer_line.partner_id.id,
                                        'type': customer_line.type,
                                        'gender': customer_line.gender,
                                        'customer_id': trans_id.id,
                                    }
                                    self.env['tour.customer.details'].create(cust_vals)
            for cust_line in obj.tour_customer_ids:
                if cust_line.i_flag == True:
                    print("Insurance")
                if cust_line.v_flag == True:
                    country_list = []
                    visa_type_list = []
                    for visa_obj in obj.tour_id.tour_destination_lines:
                        if visa_obj.is_visa == True:
                            if not visa_obj.country_id.id in country_list:
                                country_list.append(visa_obj.country_id.id)
                                visa_type_list.append(visa_obj.visa_type)
                    lenth = len(country_list)
                    for i in range(0, lenth):
                        if visa_type_list[i] == 'single':
                            self._cr.execute("""select id from visa_scheme where name='Tourist Visa(Single Entry)'""")
                            visa_id = self._cr.fetchone()
                            print("Scheme", visa_id[0])
                            self._cr.execute(
                                """select service_cost from visa_scheme where name='Tourist Visa(Single Entry)'""")
                            visa_cost = self._cr.fetchone()
                            visa_cost = get_price(self, pricelist_id, visa_cost[0])

                            print("Scheme", visa_cost)
                        else:
                            self._cr.execute("""select id from visa_scheme where name='Tourist Visa(Multiple Entry)'""")
                            visa_id = self._cr.fetchone()
                            print("Scheme", visa_id[0])
                            self._cr.execute(
                                """select service_cost from visa_scheme where name='Tourist Visa(Multiple Entry)'""")
                            visa_cost = self._cr.fetchone()
                            visa_cost = get_price(self, pricelist_id, visa_cost[0])

                            print("Scheme", visa_cost)
                        vals = {
                            'customer_id': cust_line.partner_id.id,
                            'current_date': obj.current_date,
                            'email_id': cust_line.partner_id.email,
                            'mobile': cust_line.partner_id.mobile,
                            'country_id': country_list[i],
                            'product_id': v_id[0],
                            'scheme_id': visa_id[0],
                            'service_charge': visa_cost,
                            'tour_book_id': obj.id,
                            'tour_id': obj.tour_id.id,
                            'tour_date': obj.tour_dates_id.start_date,
                            'pricelist_id': pricelist_id,
                        }
                        self.env['visa.booking'].create(vals)
                if cust_line.p_flag == True:
                    print("Passport")
                    if not (type(s_cost) == float):
                        s_cost = s_cost[0]
                    s_cost = get_price(self, pricelist_id, s_cost)
                    vals = {
                        'customer_id': cust_line.partner_id.id,
                        'current_date': obj.current_date,
                        'email_id': cust_line.partner_id.email,
                        'mobile': cust_line.partner_id.mobile,
                        'product_id': p_id[0],
                        'scheme_id': s_id[0],
                        'service_charge': s_cost,
                        'tour_book_id': obj.id,
                        'tour_id': obj.tour_id.id,
                        'tour_date': obj.tour_dates_id.start_date,
                        'pricelist_id': pricelist_id,
                    }
                    print("vals", vals)
                    self.env['passport.booking'].create(vals)
        self.write({'state': 'booked'})

        subtot = 0
        tax_amt = 0
        tot_amt = 0
        for rec in self.tour_booking_invoice_ids:
            subtot += rec.amount_untaxed
            tax_amt += rec.amount_tax
            tot_amt += rec.amount_total

        self.subtotal = subtot
        self.tax_amt = tax_amt
        self.total_amt = tot_amt
        return True

    #     def confirm_booking(self, cr, uid, ids, *args):
    #         tot_person = 0
    #         fiscal_position = False
    #         fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
    #         for obj in self.browse(cr, uid, ids):
    #             tot_person = obj.adult + obj.child
    #             payment_amt = 0.0
    #             percen = 0.0
    #             percen = float(obj.payment_policy_id.before_book_date_perc) / 100
    #
    #             for i in range(0, len(obj.tour_sale_order_ids)):
    #                 if obj.tour_sale_order_ids[i].state == 'draft':
    #                     raise osv.except_osv(_('Error !'), _(' Please Confirm The Sale Order Before Booking'))
    #             seats = 0
    #             person = 0
    #             tour_booking_flag = False
    #             for i in range(0, len(obj.tour_booking_invoice_ids)):
    #                 if obj.tour_booking_invoice_ids[i].state == 'draft':
    #                     raise osv.except_osv(_('Error !'), _(' Please Validate The Invoice Before Booking'))
    #                 print(obj.tour_dates_id)
    #                 if obj.tour_dates_id.book_date >= time.strftime('%Y-%m-%d'):
    #                     payment_amt = obj.tour_booking_invoice_ids[i].amount_total * percen
    #                     actual_pay = obj.tour_booking_invoice_ids[i].amount_total - payment_amt
    #                     if obj.tour_booking_invoice_ids[i].residual > actual_pay:
    #                         raise osv.except_osv(_('Error !'), _(' Please Pay The Booking Amount'))
    #                     seats = obj.tour_dates_id.available_seat
    #                     if seats == 0:
    #                         raise osv.except_osv(_('Error !'), _(' No Seats Available'))
    #                     person = seats - tot_person
    #                     self.pool.get('tour.dates').write(cr, uid, obj.tour_dates_id.id, {'available_seat':person})
    #                     tour_booking_flag = True
    #                 else:
    #                     raise osv.except_osv(_('Error !'), _('Tour Booking Is Closed'))
    #
    #             cr.execute('insert into tour_booking_customer_rel(tour_booking_customer_id,tour_id) values (%s,%s)', (obj.tour_id.id, obj.id))
    #             cr.execute("""select id from product_template where name='Passport'""")
    #             p_id = cr.fetchone()
    #             cr.execute("""select id from product_template where name='Visa'""")
    #             v_id = cr.fetchone()
    #             cr.execute("""select id from service_scheme where name='Regular'""")
    #             s_id = cr.fetchone()
    #             cr.execute("""select service_cost from service_scheme where name='Regular'""")
    #             s_cost = cr.fetchone()
    #             invoice_addr_id = False
    #             pricelist_id = obj.pricelist_id.id
    #             for hot_line in obj.tour_id.tour_destination_lines:
    #                 for lines in hot_line.hotel_lines:
    #                     print(lines.room_type_id, "lines.room_type_id")
    #                     if lines.name:
    #                         room_rent = hotel_rent = 0.00
    #                         if lines.room_type_id.seller_ids:
    #                             for line in lines.room_type_id.seller_ids:
    #                                 if line.name.id == lines.hotel_id.id:
    #                                     room_rent = get_price(self, cr, uid, ids, pricelist_id, line.price)
    #                                     hotel_rent = get_price(self, cr, uid, ids, pricelist_id, line.sale_price)
    #
    #                         vals = {
    #                                'customer_id': obj.customer_id.id,
    #                                'current_date':obj.current_date,
    # #                               'address_id': obj.address_id.id,
    #                                'email_id':obj.email_id,
    #                                'mobile':obj.mobile1,
    #                                'adult':obj.adult,
    #                                'child':obj.child,
    #                                'hotel_type_id':lines.hotel_type_id.id,
    #                                'hotel_id':lines.hotel_id.id,
    #                                'room_type_id':lines.room_type_id.id,
    #                                'room_rent':room_rent,
    #                                'hotel_rent':hotel_rent,
    #                                'tour_id':obj.tour_id.id,
    #                                'tour_book_id':obj.id,
    #                                'tour_start_date':obj.tour_dates_id.id,
    #                                'destination_id':hot_line.destination_id.id,
    #                                'pricelist_id':pricelist_id,
    #                                 }
    #                         print("hotel vals", vals)
    #                         hot_id = self.pool.get('tour.hotel.reservation').create(cr, uid, vals)
    #                         tax_id = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, lines.room_type_id.taxes_id)
    #                         if tax_id:
    #                             for txid in tax_id:
    #                                 cr.execute('insert into hotel_reservation_tax(hotel_res_id,tax_id) values (%s,%s)', (hot_id, txid))
    #                         for customer_line in obj.tour_customer_ids:
    #
    #                             if customer_line.h_flag == True:
    #                                 cust_vals = {
    #                                               'name':customer_line.name,
    #                                               'partner_id':customer_line.partner_id.id,
    #                                               'type':customer_line.type,
    #                                               'gender':customer_line.gender,
    #                                               'hotel_res_id':hot_id,
    #                                               }
    #                                 self.pool.get('tour.customer.details').create(cr, uid, cust_vals)
    #             transport = False
    #             for cust_line in obj.tour_customer_ids:
    #                 if cust_line.t_flag == True:
    #                     transport = True
    #             if transport:
    #                 for hot_line in obj.tour_id.tour_road_travel_lines:
    #                     for lines in hot_line.provider_ids:
    #                         if lines.name:
    #
    #                             cost_price = 0.00
    #                             sale_price = 0.00
    #                             cost_price_child = 0.00
    #                             sale_price_child = 0.00
    #                             if lines.provider_id.transport_type_info_ids:
    #                                 for line in lines.provider_id.transport_type_info_ids:
    #                                     if (line.from_date <= obj.current_date and obj.current_date <= line.to_date and line.transport_carrier_id.id == lines.transport_carrier_id.id and
    #                                          line.transport_type_id.id == hot_line.transport_type_id.id and line.travel_class_id.id == hot_line.travel_class_id.id and
    #                                          line.from_destination_id.id == hot_line.from_destination_id.id and line.to_destination_id.id == hot_line.to_destination_id.id):
    #                                         cost_price = get_price(self, cr, uid, ids, pricelist_id, line.cost_price)
    #                                         sale_price = get_price(self, cr, uid, ids, pricelist_id, line.sale_price)
    #                                         cost_price_child = get_price(self, cr, uid, ids, pricelist_id, line.cost_price_child)
    #                                         sale_price_child = get_price(self, cr, uid, ids, pricelist_id, line.sale_price_child)
    #                             vals = {
    #                                    'customer_id': obj.customer_id.id,
    #                                    'current_date':obj.current_date,
    #                                    'email_id':obj.email_id,
    #                                    'mobile':obj.mobile1,
    #                                    'adult':obj.adult,
    #                                    'child':obj.child,
    #                                    'transport_id':lines.provider_id.id,
    #                                    'transport_carrier_id':lines.transport_carrier_id.id,
    #                                    'transport_type_id':hot_line.transport_type_id.id,
    #                                    'travel_class_id':hot_line.travel_class_id.id,
    #                                    'from_destination_id':hot_line.from_destination_id.id,
    #                                    'to_destination_id':hot_line.to_destination_id.id,
    #                                    'tour_id':obj.tour_id.id,
    #                                    'tour_book_id':obj.id,
    #                                    'start_date':obj.tour_dates_id.id,
    #                                    'pricelist_id':pricelist_id,
    #                                    'cost_price':cost_price,
    #                                    'sale_price':sale_price,
    #                                    'cost_price_child':cost_price_child,
    #                                    'sale_price_child':sale_price_child,
    #                                     }
    #                             print("Transport vals", vals)
    #                             trans_id = self.pool.get('transport.book').create(cr, uid, vals)
    #
    #                             tax_id = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, hot_line.transport_type_id.taxes_id)
    #                             if tax_id:
    #                                 for txid in tax_id:
    #                                     cr.execute('insert into transport_book_tax(transport_type_id,tax_id) values (%s,%s)', (trans_id, txid))
    #
    #                             for customer_line in obj.tour_customer_ids:
    #                                 if customer_line.t_flag == True:
    #                                     cust_vals = {
    #                                                   'name':customer_line.name,
    #                                                   'partner_id':customer_line.partner_id.id,
    #                                                   'type':customer_line.type,
    #                                                   'gender':customer_line.gender,
    #                                                   'customer_id':trans_id,
    #                                                   }
    #                                     self.pool.get('tour.customer.details').create(cr, uid, cust_vals)
    #             mobile_data = ''
    #             email_data = ''
    #             for cust_line in obj.tour_customer_ids:
    #                 if cust_line.i_flag == True:
    #                         print("Insurance")
    #                 if cust_line.v_flag == True:
    #                         country_list = []
    #                         visa_type_list = []
    #                         for visa_obj in obj.tour_id.tour_destination_lines:
    #                             if visa_obj.is_visa == True:
    #                                 if not visa_obj.country_id.id in country_list:
    #                                     country_list.append(visa_obj.country_id.id)
    #                                     visa_type_list.append(visa_obj.visa_type)
    #                         lenth = len(country_list)
    #                         for i in range(0, lenth):
    #                             if visa_type_list[i] == 'single':
    #                                 cr.execute("""select id from visa_scheme where name='Tourist Visa(Single Entry)'""")
    #                                 visa_id = cr.fetchone()
    #                                 print("Scheme", visa_id[0])
    #                                 cr.execute("""select service_cost from visa_scheme where name='Tourist Visa(Single Entry)'""")
    #                                 visa_cost = cr.fetchone()
    #                                 visa_cost = get_price(self, cr, uid, ids, pricelist_id, visa_cost[0])
    #
    #                                 print("Scheme", visa_cost)
    #                             else:
    #                                 cr.execute("""select id from visa_scheme where name='Tourist Visa(Multiple Entry)'""")
    #                                 visa_id = cr.fetchone()
    #                                 print("Scheme", visa_id[0])
    #                                 cr.execute("""select service_cost from visa_scheme where name='Tourist Visa(Multiple Entry)'""")
    #                                 visa_cost = cr.fetchone()
    #                                 visa_cost = get_price(self, cr, uid, ids, pricelist_id, visa_cost[0])
    #
    #                                 print("Scheme", visa_cost)
    #                             product_visa_id =  self.pool.get('product.template').search(cr, uid, [('name','=','Visa')])
    #                             vals = {
    #                                    'customer_id': cust_line.partner_id.id,
    #                                    'current_date':obj.current_date,
    #                                    'email_id':cust_line.partner_id.email,
    #                                    'mobile':cust_line.partner_id.mobile,
    #                                    'country_id':country_list[i],
    #                                    'product_id':v_id[0],
    #                                    'scheme_id':visa_id[0],
    #                                    'service_charge':visa_cost,
    #                                    'tour_book_id':obj.id,
    #                                    'tour_id':obj.tour_id.id,
    #                                     'tour_date':obj.tour_dates_id.start_date,
    #                                    'pricelist_id':pricelist_id,
    #                                    }
    #                             self.pool.get('visa.booking').create(cr, uid, vals)
    #                 if cust_line.p_flag == True:
    #                     print("Passport")
    #                     product_passport_id =  self.pool.get('product.template').search(cr, uid, [('name','=','Passport')])
    #                     if not (type(s_cost) == float):
    #                         s_cost = s_cost[0]
    #                     s_cost = get_price(self, cr, uid, ids, pricelist_id, s_cost)
    #                     vals = {
    #                            'customer_id': cust_line.partner_id.id,
    #                            'current_date':obj.current_date,
    #                            'email_id':cust_line.partner_id.email,
    #                            'mobile':cust_line.partner_id.mobile,
    #                            'product_id': p_id[0],
    #                            'scheme_id':s_id[0],
    #                            'service_charge':s_cost,
    #                            'tour_book_id':obj.id,
    #                            'tour_id':obj.tour_id.id,
    #                            'tour_date':obj.tour_dates_id.start_date,
    #                            'pricelist_id':pricelist_id,
    #                                    }
    #                     print("vals", vals)
    #                     self.pool.get('passport.booking').create(cr, uid, vals)
    #         self.write(cr, uid, ids, {'state':'booked'})
    #         return True

    @api.multi
    def check_payment(self):
        for obj in self:
            tot_person = obj.adult + obj.child
            payment_amt = 0.0
            percen = 0.0
            percen = float(obj.payment_policy_id.before_book_date_perc) / 100
            payment_amt = float(obj.total_amt) * percen
            actual_pay = float(obj.total_amt) - payment_amt
            date=time.strftime('%Y-%m-%d')
            date= datetime.strptime(date, '%Y-%m-%d').date()

            if obj.tour_dates_id.season_id.id == obj.season_id.id and obj.tour_dates_id.due_date < date:
                raise UserError('Due Date of Payment is Crossed')
            for i in range(0, len(obj.tour_booking_invoice_ids)):
                if obj.tour_booking_invoice_ids[i].residual != 0:
                    raise UserError(' Please Pay The Remaining Amount')
        self.write({'state': 'invoiced'})

        return True

    #     def check_payment(self, cr, uid, ids, *args):
    #         for obj in self.browse(cr, uid, ids):
    #             tot_person = obj.adult + obj.child
    #             payment_amt = 0.0
    #             percen = 0.0
    #             percen = float(obj.payment_policy_id.before_book_date_perc) / 100
    #             payment_amt = float(obj.total_amt) * percen
    #             actual_pay = float(obj.total_amt) - payment_amt
    #             if obj.tour_dates_id.season_id.id == obj.season_id.id and obj.tour_dates_id.due_date < time.strftime('%Y-%m-%d'):
    #                 raise osv.except_osv(_('Error !'), _('Due Date of Payment is Crossed'))
    #             for i in range(0, len(obj.tour_booking_invoice_ids)):
    #                 if obj.tour_booking_invoice_ids[i].residual != 0:
    #                     raise osv.except_osv(_('Error !'), _(' Please Pay The Remaining Amount'))
    #         self.write(cr, uid, ids, {'state':'invoiced'})
    #         return True

    def action_done(self):
        objs = self
        obj = objs[0]
        hot_id = self.env['tour.hotel.reservation'].search([('tour_book_id', '=', obj.id)])
        if hot_id:
            hot_browse = hot_id
            for hotel_id in hot_browse:
                if hotel_id.state != 'done':
                    raise UserError('Associated Hotel Booking No  "%s" is not in done State.' % (hotel_id.name))
        transport_id = self.env['transport.book'].search([('tour_book_id', '=', obj.id)])
        if transport_id:
            transport_browse = transport_id
            for tran_id in transport_browse:
                if tran_id.state != 'done':
                    raise UserError('Associated Transport Booking No  "%s" is not in done State.' % (tran_id.name,))
        visa_id = self.env['visa.booking'].search([('tour_book_id', '=', obj.id)])
        if visa_id:
            visa_browse = visa_id
            for visa in visa_browse:
                if visa.state != 'done':
                    raise UserError('Associated Visa Booking No  "%s" is not in done State.' % (visa.name,))
        passport_id = self.env['visa.booking'].search([('tour_book_id', '=', obj.id)])
        if passport_id:
            pass_browse = passport_id
            for passport in pass_browse:
                if passport.state != 'done':
                    raise UserError('Associated Passport Booking No  "%s" is not in done State.' % (passport.name,))

        self.write({'state': 'done'})
        return True


#     def action_done(self, cr, uid, ids, *args):
#         objs = self.browse(cr, uid, ids)
#         obj = objs[0]
#         hot_id = self.pool.get('tour.hotel.reservation').search(cr, uid, [('tour_book_id', '=', obj.id)])
#         if hot_id:
#             hot_browse = self.pool.get('tour.hotel.reservation').browse(cr, uid, hot_id)
#             for hotel_id in hot_browse:
#                 if hotel_id.state != 'done':
#                     raise osv.except_osv(_('Error !'),
#                             _('Associated Hotel Booking No  "%s" is not in done State.') % (hotel_id.name,))
#         transport_id = self.pool.get('transport.book').search(cr, uid, [('tour_book_id', '=', obj.id)])
#         if transport_id:
#             transport_browse = self.pool.get('transport.book').browse(cr, uid, transport_id)
#             for tran_id in transport_browse:
#                 if tran_id.state != 'done':
#                     raise osv.except_osv(_('Error !'),
#                             _('Associated Transport Booking No  "%s" is not in done State.') % (tran_id.name,))
#         visa_id = self.pool.get('visa.booking').search(cr, uid, [('tour_book_id', '=', obj.id)])
#         if visa_id:
#             visa_browse = self.pool.get('visa.booking').browse(cr, uid, visa_id)
#             for visa in visa_browse:
#                 if visa.state != 'done':
#                     raise osv.except_osv(_('Error !'),
#                             _('Associated Visa Booking No  "%s" is not in done State.') % (visa.name,))
#         passport_id = self.pool.get('visa.booking').search(cr, uid, [('tour_book_id', '=', obj.id)])
#         if passport_id:
#             pass_browse = self.pool.get('visa.booking').browse(cr, uid, passport_id)
#             for passport in pass_browse:
#                 if passport.state != 'done':
#                     raise osv.except_osv(_('Error !'),
#                             _('Associated Passport Booking No  "%s" is not in done State.') % (passport.name,))
#         
#         
#         self.write(cr, uid, ids, {'state':'done'}) 
#         return True 


class tour_insurance_line(models.Model):
    _name = "tour.insurance.line"
    _description = "Tour Insurance Lines"

    @api.depends('insurance_policy_id')
    def _get_insurance_cost(self):
        print("dfghdfjkhgkdjfgdhfg")
        res = {}
        obj = self[0]
        adult_cost = get_price(self, obj.tour_book_id.pricelist_id.id,
                               obj.insurance_policy_id.insurance_cost_for_adults)
        child_cost = get_price(self, obj.tour_book_id.pricelist_id.id,
                               obj.insurance_policy_id.insurance_cost_for_childs)
        self.insurance_cost = (adult_cost * obj.name) + (child_cost * obj.child_coverage1)

        if obj.tour_book_id.adult < obj.name:
            raise Warning('Check Adult Persons For Policy Coverage ')
        if obj.tour_book_id.child < obj.child_coverage1:
            #             pass
            raise UserWarning('Check Child For Policy Coverage ')



    #     def _get_insurance_cost(self, cr, uid, ids, args1, args2, context=None):
    #         res = {}
    #         total = 0
    #         adult_cost = 0
    #         child_cost = 0
    #         obj = self.browse(cr, uid, ids)[0]
    #         adult_cost = get_price(self, cr, uid, ids, obj.tour_book_id.pricelist_id.id, obj.insurance_policy_id.insurance_cost_for_adults)
    #         child_cost = get_price(self, cr, uid, ids, obj.tour_book_id.pricelist_id.id, obj.insurance_policy_id.insurance_cost_for_childs)
    #         total = (adult_cost * obj.name) + (child_cost * obj.child_coverage1)
    #         if obj.tour_book_id.adult < obj.name:
    #             raise osv.except_osv(_('Error !'), _('Check Adult Persons For Policy Coverage '))
    #         if obj.tour_book_id.child < obj.child_coverage1:
    #             raise osv.except_osv(_('Error !'), _('Check Child For Policy Coverage '))
    #         res[obj.id] = total
    #         return res

    insurance_policy_id = fields.Many2one('insurance.policy', "Insurance Policy", required=True)
    name = fields.Integer("Adult Policy Coverage")
    child_coverage1 = fields.Integer("Child Policy Coverage")
    insurance_cost = fields.Float(compute=_get_insurance_cost, string="Total Cost", store=True)
    tour_book_id = fields.Many2one('tour.booking', string='Tour Book ID')


class tour_customer_details(models.Model):
    _name = "tour.customer.details"
    _description = "Tour Customer Details"

    name = fields.Char("Age", size=50, required=True)
    partner_id = fields.Many2one("res.partner", "Customer")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Gender', default=lambda *a: 'male')
    type = fields.Selection([
        ('adult', 'Adult'),
        ('child', 'Child'),
    ], string='Adult/Child', default=lambda *a: 'adult')
    h_flag = fields.Boolean('H', help="For Hotel Reservation Line")
    t_flag = fields.Boolean('T', help="For Transport Reservation Line")
    i_flag = fields.Boolean('I', help="For Insurance Reservation Line")
    v_flag = fields.Boolean('V', help="For Visa Reservation Line")
    p_flag = fields.Boolean('P', help="For Passport Reservation Line")
    tour_book_id = fields.Many2one('tour.booking', 'Tour Book ID')
    customer_id = fields.Many2one('transport.book', 'Transport Booking Ref')
    state = fields.Selection([
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancelled'),
    ], string='Status', default=lambda *a: 'confirm')

    #     _defaults = {
    #                  'gender': lambda * a: 'male',
    #                  'type': lambda * a: 'adult',
    #                  'state': lambda * a: 'confirm',
    #                  }

    @api.model
    def create(self, vals):
        """
        To override create method
        """
        if 'tour_book_id' in vals:
            obj = self.env['tour.booking'].browse(vals['tour_book_id'])
            visa = False
            hotel = False
            transport = False
            for visa_line in obj.tour_id.tour_destination_lines:
                if visa_line.is_visa == True:
                    visa = True
                    break
            for hotel_line in obj.tour_id.tour_destination_lines:
                if hotel_line.hotel_lines:
                    hotel = True
                    break
            for travel_line in obj.tour_id.tour_road_travel_lines:
                if travel_line.provider_ids:
                    transport = True
                    break
            vals.update({'v_flag': visa, 'h_flag': hotel, 't_flag': transport, })
        return super(tour_customer_details, self).create(vals)


#     def create(self, cr, uid, vals, context=None):
#         """
#         To override create method
#         """
#         if vals.__contains__('tour_book_id'):
#             if vals['tour_book_id']:
#                 obj = self.pool.get('tour.booking').browse(cr, uid, vals['tour_book_id'])
#                 print(obj, "obj")
#                 visa = False
#                 hotel = False
#                 transport = False
#                 for visa_line in obj.tour_id.tour_destination_lines:
#                     if visa_line.is_visa == True:
#                         visa = True
#                         break
#                 for hotel_line in obj.tour_id.tour_destination_lines:
#                     if hotel_line.hotel_lines:
#                         hotel = True
#                         break
#                 for travel_line in obj.tour_id.tour_road_travel_lines:
#                     if travel_line.provider_ids:
#                         transport = True
#                         break
#                 vals.update({'v_flag': visa, 'h_flag':hotel, 't_flag':transport, })
#         return super(tour_customer_details, self).create(cr, uid, vals, context=context)


class product_product(models.Model):
    _inherit = "product.product"

    is_tour = fields.Boolean("Is Tour")


class tour_travel(models.Model):
    _name = "tour.travel"
    _description = "Tour And Travel Management"

    name = fields.Char("Name", size=50, required=True)
    description = fields.Char("Description", size=60)


class carrier_type(models.Model):
    _name = "carrier.type"
    _description = "Carrier Type"

    name = fields.Char("Name", size=64, required=True)
    description = fields.Char("Code", size=10)


class sale_order(models.Model):
    _inherit = "sale.order"

    def get_start_date_tour(self, tour_book_id):
        print('*******Enter')
        got_it = self.env['tour.booking'].search([('name', '=', tour_book_id.name)])
        return got_it.tour_dates_id.name

    #     def get_start_date_tour(self,cr,uid,ids,tour_book_id):
    #         print('*******Enter')
    #         got_it = self.pool.get('tour.booking').search(cr,uid,[('name','=',tour_book_id.name)])
    #         print('********Done now returning\n',got_it)
    #         got_it = self.pool.get('tour.booking').browse(cr,uid,got_it)
    #         print('******Gottt',got_it,got_it.tour_dates_id.name)
    #         return got_it.tour_dates_id.name

    def get_partner_lang_date(self, date1, lang):
        search_id = self.env['res.lang'].search([('code', '=', lang)])
        record = search_id
        new_date = datetime.strftime(datetime.strptime(str(date1), '%Y-%m-%d %H:%M:%S'), record.date_format)
        return new_date

    #     def get_partner_lang_date(self, cr, uid, ids, date1,lang):
    #         search_id = self.pool.get('res.lang').search(cr,uid,[('code','=',lang)])
    #         record=self.pool.get('res.lang').browse(cr,uid,search_id)
    #         print("!!!!!!!!!!! dffddf",date1,record.date_format)
    # #         date1 = str(date1.date())
    #         print("!!!!!!!!!!!!!!!!!! ",date1)
    #         new_date=datetime.strftime(datetime.strptime(date1,'%Y-%m-%d %H:%M:%S'),record.date_format)
    #         print("!!!!!!!!!!!!!!!!---new date=",new_date)
    #         return new_date

    @api.model
    def create(self, vals, ):
        # function overwrites create method and auto generate request no.
        vals['name'] = self.env['ir.sequence'].get('sale.order')
        return super(sale_order, self).create(vals)

    #     def create(self, cr, uid, vals, context=None):
    #         # function overwrites create method and auto generate request no.
    #         vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order')
    #         return super(sale_order, self).create(cr, uid, vals, context=context)

    tour_book_id = fields.Many2one("tour.booking", "Ref Tour Book Id ")
    name = fields.Char('Order Reference', size=64, required=True, readonly=True,
                       states={'draft': [('readonly', False)]}, select=True)
    tour_id = fields.Many2one('tour.package', 'Tour', required=True)

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        res = super(sale_order, self).action_invoice_create(grouped, final)
        inv_obj = self.env['account.invoice']
        sale_obj = self.env['sale.order']
        for o in inv_obj.browse(res):
            o.write({'tour_product_id': self.tour_id.id})
            sale_id = sale_obj.search([('name', '=', o.origin)])
            if sale_id.tour_book_id.id:
                self._cr.execute('insert into tour_booking_invoice_rel(tour_booking_id,invoice_id) values (%s,%s)',
                                 (sale_id.tour_book_id.id, res[0]))
        return res


#     def action_invoice_create(self, cr, uid, ids, grouped=False, states=['confirmed', 'done', 'exception'], date_inv = False, context=None):

#         res = False
#         invoices = {}
#         invoice_ids = []
#         picking_obj = self.pool.get('stock.picking')
#         invoice = self.pool.get('account.invoice')
#         obj_sale_order_line = self.pool.get('sale.order.line')
#         if context is None:
#             context = {}
#         # If date was specified, use it as date invoiced, usefull when invoices are generated this month and put the
#         # last day of the last month as invoice date
#         if date_inv:
#             context['date_inv'] = date_inv
#         for o in self.browse(cr, uid, ids, context=context):
#             lines = []
#             for line in o.order_line:
#                 print line, '---------------------1111'
# #                 if line.invoiced:
# #                     continue
# #                 elif (line.state in states):
# #                     lines.append(line.id)
#                 created_lines = obj_sale_order_line.invoice_line_create(line.qty_to_invoice)
#             if created_lines:
#                 invoices.setdefault(o.partner_id.id, []).append((o, created_lines))
#         if not invoices:
#             for o in self.browse(cr, uid, ids, context=context):
#                 for i in o.invoice_ids:
#                     if i.state == 'draft':
#                         return i.id
#         for val in invoices.values():
#             if grouped:
#                 res = self._make_invoice(cr, uid, val[0][0], reduce(lambda x, y: x + y, [l for o, l in val], []), context=context)
#                 invoice_ref = ''
#                 for o, l in val:
#                     invoice_ref += o.name + '|'
#                     self.write(cr, uid, [o.id], {'state': 'progress'})
#                     if o.order_policy == 'picking':
#                         picking_obj.write(cr, uid, map(lambda x: x.id, o.picking_ids), {'invoice_state': 'invoiced'})
#                     cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (o.id, res))
#                 invoice.write(cr, uid, [res], {'origin': invoice_ref, 'name': invoice_ref})
#             else:
#                 for order, il in val:
#                     res = self._make_invoice(cr, uid, order, il, context=context)
#                     invoice_ids.append(res)
#                     self.write(cr, uid, [order.id], {'state': 'progress'})
#                     if order.order_policy == 'picking':
#                         picking_obj.write(cr, uid, map(lambda x: x.id, order.picking_ids), {'invoice_state': 'invoiced'})
#                     cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (order.id, res))
#                     if order.tour_book_id.id:
#                         cr.execute('insert into tour_booking_invoice_rel(tour_booking_id,invoice_id) values (%s,%s)', (order.tour_book_id.id, res))
#         return res


class tour_package_products_line(models.Model):
    _name = 'tour.package.products.line'
    _description='Tour Package Products Line'

    @api.multi
    @api.depends('price_unit','qty','tax_id')
    def _amount_line(self):
        res = {}

        taxes = {}
        if self._context is None:
            self._context = {}

        for line in self:
            price = line.price_unit
            self.price_subtotal=self.price_unit * self.qty
            taxes = line.tax_id.compute_all(price, None, line.qty, line.product_id)
            res[line.id] = {
                'price_subtotal': 0.0,
                'untaxed_amt': 0.0,
                'tax_amt': 0.0,
            }
            """
                The tax_obj.compute_all method returns the following dictionary..........
        RETURN: {
                    'total': 0.0,                # Total without taxes
                    'total_included: 0.0,        # Total with taxes
                    'taxes': []                  # List of taxes, see compute for the format
                }
        """
            res[line.id]["price_subtotal"] = taxes['total_excluded']
            res[line.id]["total_with_tax"] = taxes['total_included']
            total_tax = 0.0

            for tax in taxes['taxes']:
                total_tax = total_tax + tax['amount']
            res[line.id]["tax_amt"] = total_tax
        return res

    #     def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
    #         tax_obj = self.pool.get('account.tax')
    #         res = {}
    #         taxes = {}
    #         if context is None:
    #             context = {}
    #         for line in self.browse(cr, uid, ids, context=context):
    #             price = line.price_unit
    #             taxes = line.tax_id.compute_all(price, None, line.qty, line.product_id)
    #             res[line.id] = {
    #                 'price_subtotal': 0.0,
    #                 'untaxed_amt': 0.0,
    #                 'tax_amt': 0.0,
    #             }
    #             """
    #                 The tax_obj.compute_all method returns the following dictionary..........
    #         RETURN: {
    #                     'total': 0.0,                # Total without taxes
    #                     'total_included: 0.0,        # Total with taxes
    #                     'taxes': []                  # List of taxes, see compute for the format
    #                 }
    #         """
    #             res[line.id]["price_subtotal"] = taxes['total_excluded']
    #             res[line.id]["total_with_tax"] = taxes['total_included']
    #             total_tax = 0.0
    #
    #             for  tax in taxes['taxes']:
    #                 total_tax = total_tax + tax['amount']
    #             res[line.id]["tax_amt"] = total_tax
    #         return res

    @api.onchange('product_id')
    def product_id_change(self):
        res = {}
        if self.product_id:
            res['price_unit'] = self.product_id.list_price
            res['price_subtotal'] = 0.0
            res['name'] = self.product_id.name
            taxes = []
            if self.product_id.taxes_id:
                for tax in self.product_id.taxes_id:
                    taxes.append(tax.id)
                if taxes:
                    res['tax_id'] = taxes

        print(res)
        return {'value': res}

    #     def product_id_change(self, cr, uid, ids, product, qty=0, name='', context=None):
    #         res = {}
    #
    #         product_obj = self.pool.get('product.product')
    #         for product in product_obj.browse(cr, uid, [product]):
    #             res['price_unit'] = product.list_price
    #             res['price_subtotal'] = 0.0
    #             res['name'] = product.name_template
    #             taxes = []
    #             if product.taxes_id:
    #                 for tax in product.taxes_id:
    #                     taxes.append(tax.id)
    #                 if taxes:
    #                     res['tax_id'] = taxes
    #
    #         print(res)
    #         return {'value' : res}

    tour_package_id = fields.Many2one('tour.package', 'Tour Package')
    tour_booking_id = fields.Many2one('tour.booking', 'Tour Booking')
    product_id = fields.Many2one('product.product', 'Product')
    name = fields.Text('Description', required=True)
    qty = fields.Float('Quantity', required=True)
    price_unit = fields.Float('Unit Price', required=True)
    tax_id = fields.Many2many('account.tax', 'account_tax_id', 'tour_package_products_line_id', 'tax_id', 'Taxes')
    total_with_tax = fields.Float(compute=_amount_line, string='Total With Tax', multi='sums', store=True)
    tax_amt = fields.Float(compute=_amount_line, string='Taxed Amount', multi='sums', store=True)
    price_subtotal = fields.Float(compute=_amount_line, string='Subtotal', multi='sums', store=True,
                                  track_visibility='always')


class res_partner(models.Model):
    _inherit = "res.partner"

    tour_partner_history_ids = fields.Many2many('tour.booking', 'tour_partner_history_rel', 'tour_booking_id',
                                                'partner_id', 'Tour History', readonly=True)
    agent = fields.Boolean("Agent")
    is_hotel = fields.Boolean("Hotel")
    hotel_type_id = fields.Many2one("hotel.type", "Hotel Type")
    email_list_ids = fields.Many2many("email.list", "email_res", "email_id", "res_id", "Email List")
    commission_line_ids = fields.One2many('agent.commission.line', 'agent_id', 'Transport Id')
    
    
    
    
    
    


class agent_commission_line(models.Model):
    _name = "agent.commission.line"
    _description = "Agent Commission Line"

    name = fields.Char('Tour Name', size=164, required=True)
    tour_id = fields.Many2one('tour.package', 'Tour', required=True)
    percentage = fields.Integer("Commission Percentage", required=True)
    agent_id = fields.Many2one('res.partner', 'Partner Id')

    @api.onchange('tour_id')
    def on_change_tour_id(self):
        result = {}
        result['name'] = self.tour_id.name1
        return {'value': result}


#     def on_change_tour_id(self, cr, uid, ids, tour_id):
#         result = {}
#         obj = self.pool.get('tour.package').browse(cr, uid, tour_id)
#         result['name'] = obj.name1
#         return {'value': result}


class ir_attachment(models.Model):
    _inherit = "ir.attachment"
    _description = "Attachments Inherit For Hotel"

    hotel_customer_id = fields.Many2one('tour.hotel.info', 'Hotel ID')


class visa_booking(models.Model):
    _inherit = "visa.booking"
    _description = "Visa Booking"

    tour_book_id = fields.Many2one('tour.booking', 'Tour Booking Ref')


class account_invoice(models.Model):
    _inherit = "account.invoice"

    tour_product_id = fields.Many2one('tour.package', string='Tour Name')

    def get_start_date_tour(self, origin_id):
        sale_order_ids = self.env['sale.order'].search([('name', '=', origin_id)])
        sale_order_idss = sale_order_ids
        got_it = self.env['tour.booking'].search([('name', '=', sale_order_idss.tour_book_id.name)])
        return got_it.tour_dates_id.name

    #     def get_start_date_tour(self,cr,uid,ids,origin_id):
    #         print('******Origin id...',origin_id)
    #         sale_order_ids = self.pool.get('sale.order').search(cr,uid,[('name','=',origin_id)])
    #         sale_order_idss = self.pool.get('sale.order').browse(cr,uid,sale_order_ids)
    #         print('***********Gottttt',sale_order_idss.tour_book_id.name)
    #         got_it = self.pool.get('tour.booking').search(cr,uid,[('name','=',sale_order_idss.tour_book_id.name)])
    #         print('********Done now returning\n',got_it)
    #         got_it = self.pool.get('tour.booking').browse(cr,uid,got_it)
    #         print('******Gottt',got_it,got_it.tour_dates_id.name)
    #         return got_it.tour_dates_id.name

    def get_partner_lang_date(self, date1, lang):
        search_id = self.env['res.lang'].search([('code', '=', lang)])
        record = search_id
        new_date = datetime.strftime(datetime.strptime(date1, '%Y-%m-%d'), record.date_format)
        return new_date

    #     def get_partner_lang_date(self, cr, uid, ids, date1,lang):
    #         search_id = self.pool.get('res.lang').search(cr,uid,[('code','=',lang)])
    #         record=self.pool.get('res.lang').browse(cr,uid,search_id)
    #         print("!!!!!!!!!!!!!zzzzz-----",record.date_format,date1)
    #         new_date=datetime.strftime(datetime.strptime(date1,'%Y-%m-%d'),record.date_format)
    #         print("!!!!!!!!!!!!!!!!---new date=",new_date)
    #         return new_date

    def action_invoice_sent(self):
        '''
        This function opens a window to compose an email, with the edi invoice template message loaded by default
        '''
        assert len(self._ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('tour_travel', 'email_template_edi_invoice_inherited')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self._context)
        ctx.update({
            'default_model': 'account.invoice',
            'default_res_id': self._ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id.id,
            'default_composition_mode': 'comment',
            'mark_invoice_as_sent': True,
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


#     def action_invoice_sent(self, cr, uid, ids, context=None):
#         '''
#         This function opens a window to compose an email, with the edi invoice template message loaded by default
#         '''
#         assert len(ids) == 1, 'This option should only be used for a single id at a time.'
#         ir_model_data = self.pool.get('ir.model.data')
#         try:
#             template_id = ir_model_data.get_object_reference(cr, uid, 'tour_travel', 'email_template_edi_invoice_inherited')[1]
#         except ValueError:
#             template_id = False
#         try:
#             compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
#         except ValueError:
#             compose_form_id = False
#         ctx = dict(context)
#         ctx.update({
#             'default_model': 'account.invoice',
#             'default_res_id': ids[0],
#             'default_use_template': bool(template_id),
#             'default_template_id': template_id,
#             'default_composition_mode': 'comment',
#             'mark_invoice_as_sent': True,
#             })
#         return {
#             'type': 'ir.actions.act_window',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'mail.compose.message',
#             'views': [(compose_form_id, 'form')],
#             'view_id': compose_form_id,
#             'target': 'new',
#             'context': ctx,
#         }   


# class sale_advance_payment_inv(osv.osv_memory):
#     _inherit = "sale.advance.payment.inv"
#     _description = "Sales Advance Payment Invoice"

#     def create_invoices(self, cr, uid, ids, context=None):
#          
#         inv_ids = None 
#         sale_id = context.get('active_ids', [])
#         sale_obj = self.pool.get('sale.order')
#         for o in self.browse(cr, uid, ids):
#             if o.advance_payment_method == 'all':
#                 inv_ids = sale_obj.action_invoice_create(cr, uid, sale_id[0])
#         print inv_ids,'----------------------123'
#                  
#              
#         return super(sale_advance_payment_inv, self).create_invoices(cr, uid, ids,context)

#     def create_invoices(self, cr, uid, ids, context=None):
#         """ create invoices for the active sales orders """
#         sale_obj = self.pool.get('sale.order')
#         act_window = self.pool.get('ir.actions.act_window')
#         wizard = self.browse(cr, uid, ids[0], context)
#         sale_ids = context.get('active_ids', [])
#         if wizard.advance_payment_method == 'all':
#             # create the final invoices of the active sales orders
# #             res = sale_obj.action_invoice_create(cr, uid, sale_ids, context)
#             so=self.env['sale.order'].broswe(sale_ids)
#             res=so.action_invoice_create(sale_ids)
#             
#             
#             invv = self.pool.get('account.invoice').browse(cr, uid, res['res_id'], context)
#             sale_order_search = self.pool.get('sale.order').search(cr, uid, [('name', '=', invv.origin)])
#             if sale_order_search:
#                 sale_brw = self.pool.get('sale.order').browse(cr, uid, sale_order_search, context)[0]
#                 self.pool.get('account.invoice').write(cr, uid, res['res_id'], {'tour_product_id': sale_brw.tour_id.id}, context=context)
#             if context.get('open_invoices', False):
#                 return res
#             return {'type': 'ir.actions.act_window_close'}
#         if wizard.advance_payment_method == 'lines':
#             # open the list view of sales order lines to invoice
#             res = act_window.for_xml_id(cr, uid, 'sale', 'action_order_line_tree2', context)
#             res['context'] = {
#                 'search_default_uninvoiced': 1,
#                 'search_default_order_id': sale_ids and sale_ids[0] or False,
#             }
#             return res
#         assert wizard.advance_payment_method in ('fixed', 'percentage')
#         inv_ids = []
#         for sale_id, inv_values in self._prepare_advance_invoice_vals(cr, uid, ids, context=context):
#             inv_ids.append(self._create_invoices(cr, uid, inv_values, sale_id, context=context))
#      
#         if context.get('open_invoices', False):
#             return self.open_invoices(cr, uid, ids, inv_ids, context=context)
#         return {'type': 'ir.actions.act_window_close'}
#     


class email_list(models.Model):
    _name = "email.list"
    _description = "email list"

    name = fields.Char('Email list', size=164, required=True)

    def copy(self, default=None):
        if self._context is None:
            self._context = {}

        if not default:
            default = {}

        product = self.read(['name'])
        default = default.copy()
        default.update(name=_("%s (copy)") % (product['name']))
        return super(email_list, self).copy(default=default)

#     def copy(self, cr, uid, id, default=None, context=None):
#         if context is None:
#             context = {}
# 
#         if not default:
#             default = {}
# 
#         product = self.read(cr, uid, id, ['name'], context=context)
#         default = default.copy()
#         default.update(name=_("%s (copy)") % (product['name']))
#         return super(email_list, self).copy(cr, uid, id, default=default,context=context)
