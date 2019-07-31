# -*- coding: utf-8 -*-

{
    'name': 'Sale Loyalty',
    'category': 'Sales',
    'version': '1.0',
    'summary': 'Loyalty on Sale',
    'sequence': 30,
    'description': """
        This module loyalty program and its easily managing a customer reward option with
        Discount, Voucher, Gift type loyalty.
    """,
    'author': 'Kanak Infosystems',
    'website': 'www.kanakinfosystems.com',
    'images': ['static/description/banner.jpg'],
    'depends': ['base', 'sale_management', 'point_of_sale', 'membership'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_view.xml',
        'views/sale_view.xml',
        'views/pos_loyalty_views.xml',
        'views/membership_level_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    'price': 50,
    'currency': 'EUR',
}
