# -*- coding: utf-8 -*-
{
    'name' : 'ACE UTM',
    'category': 'ACEconomy',
    'author': 'pcb-graphtech.com.vn',
    'description': 'Customize UTM',
    'depends': [
        'sale_crm',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Wizard
        # View
        'views/utm_view.xml',
        'views/crm_lead_view.xml',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        # Menu
        'menu/menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
