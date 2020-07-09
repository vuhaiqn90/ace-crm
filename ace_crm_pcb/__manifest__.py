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
        # 'ace_crm_core',
        # 'mass_mailing',
    ],
    'data': [
        # Data
        'data/ir_sequence.xml',
        'data/group.xml',
        # Security
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        # Views
        'views/res_users.xml',
        'views/menu.xml',
        'views/crm_lead_view.xml',
        # 'views/mail_mass_mailing.xml'
        # Reports
        'reports/report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
