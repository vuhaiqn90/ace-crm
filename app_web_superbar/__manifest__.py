# -*- coding: utf-8 -*-

# Created on 2019-01-04
# author: 广州尚鹏，https://www.sunpop.cn
# email: 300883@qq.com
# resource of Sunpop
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# Odoo12在线用户手册（长期更新）
# https://www.sunpop.cn/documentation/user/12.0/en/index.html

# Odoo12在线开发者手册（长期更新）
# https://www.sunpop.cn/documentation/12.0/index.html

# Odoo10在线中文用户手册（长期更新）
# https://www.sunpop.cn/documentation/user/10.0/zh_CN/index.html

# Odoo10离线中文用户手册下载
# https://www.sunpop.cn/odoo10_user_manual_document_offline/
# Odoo10离线开发手册下载-含python教程，jquery参考，Jinja2模板，PostgresSQL参考（odoo开发必备）
# https://www.sunpop.cn/odoo10_developer_document_offline/

# todo: view A有关联字段B，如果AB都有superbar，那么A->B->A，此时toggle会不显示，superbar也不显示，要调整
{
    'name': "Advance Search Sidebar with Hierarchy Parent Children Tree",
    'version': '12.19.10.30',
    'author': 'Sunpop.cn',
    'category': 'Base',
    'website': 'https://www.sunpop.cn',
    'license': 'LGPL-3',
    'sequence': 2,
    'summary': """
    Advance Search, Advance Filter with Hierarchy Tree.Parent Children relation tree.
    Easy to navigator and browse any data. Support Search more list, kanban, pivot, graph view. 
    ztree widget.Hierarchy Tree
    """,
    'description': """
    Advance Search, Advance Filter with Parent Children Tree.
    Easy to navigator and browse any data. Support list, kanban, pivot, graph view. 
    Only show when width > 992px;
    This is a Superbar suite, with zTree widget. 
    You can use to search or browse the data in any module. Like Product, CRM, Sale order, Purchase order, MRP, Inventory, Accounting vouchers, Mrp order, HR or any other module of odoo.
    Alse we have make some demo.
    超级方便的查询，树状视图导航。可用在任何模块中。
    可动态设置的domain参数，以 search_superbar_domain 开头，如：
            action['context'] = {
            'search_superbar_domain_group_id': "[('root_sale', '=', " + str(self.id) + ")]"
        }
        todo: 直接用 active id
    """,
    'price': 88.00,
    'currency': 'EUR',
    'depends': [
        'web',
        'app_web_widget_ztree',
    ],
    'images': ['static/description/banner.gif'],
    'data': [
        'views/webclient_templates.xml',
        # 'views/product_views.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'css': [
    ],
    'qweb': [
        'static/src/xml/superbar.xml',
    ],
    'js': [
    ],
    'post_load': None,
    'post_init_hook': None,
    'installable': True,
    'application': True,
    'auto_install': False,
}
