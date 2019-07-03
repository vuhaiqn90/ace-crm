# -*- coding: utf-8 -*-
{
    'name': 'ACECONOMY CRM RESELLER',
    'category': 'ACEconomy',
    'author': 'pcb-graphtech.com.vn',
    'description': '',
    'depends': [
        'ace_crm_core',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order.xml',
        'views/reseller.xml',
        'views/crm_lead.xml',
        'views/calendar.xml',
        'views/crm_phonecall.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}