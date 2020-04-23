{
    'name': "ACE TMG",
    'version': "1.0",
    'author': "vuhai@aceconomy.net",
    'category': "TMG Project",
    'description':"""
        Customize function
    """,
    'depends': ['sale_coupon', 'account'],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Views
        'views/partner_views.xml',
        'views/sale_order_view.xml',
        'views/res_users_view.xml',
        'views/commission_config_view.xml',
        'views/commission_view.xml',
        'views/account_invoice_view.xml',
        # Menu
        'menu/menu.xml',
    ],
    'demo': [],
    'installable': True,
}