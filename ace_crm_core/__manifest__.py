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
    ],
    'data': [
        'views/product.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
