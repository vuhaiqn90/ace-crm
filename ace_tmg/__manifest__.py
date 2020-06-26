{
    'name': "ACE TMG",
    'version': "1.0",
    'author': "vuhai@aceconomy.net",
    'category': "TMG Project",
    'description':"""
        Customize function
    """,
    'depends': [
        'purchase',
        'sale_coupon',
        'stock_account',
        'ace_accounting_vietnam_report',
        'partner_credit_limit',
        'ace_stock_report',
        'delivery',
    ],
    'data': [
        # Data
        'data/sequence.xml',
        'data/report_text_data.xml',
        # Security
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        # Views
        'views/partner_views.xml',
        'views/sale_order_view.xml',
        'views/res_users_view.xml',
        'views/commission_config_view.xml',
        'views/commission_view.xml',
        'views/account_invoice_view.xml',
        'views/stock_picking_view.xml',
        'views/purchase_order_view.xml',
        'views/product_view.xml',
        'views/tmg_membership_view.xml',
        # Reports
        'reports/print_receipt.xml',
        'reports/print_voucher.xml',
        'reports/ace_partner_ledger_report.xml',
        'reports/report.xml',
        # Menu
        'menu/menu.xml',
    ],
    'demo': [],
    'installable': True,
}