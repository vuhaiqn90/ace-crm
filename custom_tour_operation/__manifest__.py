# -*- coding: utf-8 -*-
{
    'name': ' Odoo  Custom Tour & Travel Management',
    "version": "12.0",
    'author': 'Pragmatic Techsoft Pvt. Ltd.',
    "website": "http://www.pragtech.co.in",
    'category': 'Generic Modules/Custom Tour',
    'description': """The generic OpenERP Custom Tour Management
""",
    'depends': ['base', 'tour_travel'],
    'data': [
        # 'wizard/add_new_sites_view.xml',
        'views/custom_tour_operation_view.xml',
        'views/coustom_tour_sequence_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    "active": False,
    'license': 'OPL-1',
}
