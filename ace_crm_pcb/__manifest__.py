# -*- coding: utf-8 -*-
{
    'name': 'ACECONOMY CRM PCB-GRAPHTECH',
    'category': 'ACEconomy',
    'author': 'pcb-graphtech.com.vn',
    'description': '',
    'depends': [
        'sale',
        'ace_crm_core',
        'mass_mailing',
    ],
    'data': [
        'data/ir_sequence.xml',
        'views/res_users.xml',
        'views/crm_lead_view.xml',
        'views/mail_mass_mailing.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
