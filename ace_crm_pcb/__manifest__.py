# -*- coding: utf-8 -*-
{
    'name': 'ACECONOMY CRM PCB-GRAPHTECH',
    'category': 'ACEconomy',
    'author': 'pcb-graphtech.com.vn',
    'description': '',
    'depends': [
        'crm',
        'sale',
        'contacts',
        'ace_crm_core',
    ],
    'data': [
        'data/ir_sequence.xml',
        'data/group.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'views/res_users.xml',
        'views/menu.xml',
        'views/crm_lead_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
