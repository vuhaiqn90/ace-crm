# -*- coding: utf-8 -*-
{
    'name': 'ACECONOMY CRM BASE',
    'category': 'ACEconomy',
    'author': 'pcb-graphtech.com.vn',
    'description': '',
    'depends': [
        'product',
        'stock',
        'calendar',
        'crm',
        'sale',
        'sale_crm',
        'crm_phonecall',
        'web_group_by_percentage',
        'web_tree_resize_column',
        'web_widget_color',
        'web_tree_dynamic_colored_field',
    ],
    'data': [
        'views/product.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
