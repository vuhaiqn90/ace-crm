{
    'name': "ACE SMS",
    'version': "1.0",
    'author': "khangnguyen16021990@gmail",
    'category': "Tools Personal",
    'summary':"""
        Allows you to send and receive smses from multiple gateways
    """,
    'description':"""
        Allows you to send and receive smses from multiple gateways
    """,
    'depends': ['sale'],
    'data': [
        # data
        'data/esms_gateway_data.xml',
        'data/esms_status_data.xml',
        'data/sms_template.xml',


        # views
        'views/ir_actions_server_view.xml',
        'views/res_partner_view.xml',
        'views/sms_brand_view.xml',
        'views/sms_gateway_view.xml',
        'views/sms_compose_view.xml',
        'views/sms_message_status_view.xml',
        'views/sms_message_view.xml',
        'views/sms_template_view.xml',
        'views/sms_marketing_group_view.xml',
        'views/sms_marketing_view.xml',

        # security
        'security/ir.model.access.csv',

        # menu
        'menus/sms_menus.xml',
    ],
    'demo': [],

    'installable': True,
}