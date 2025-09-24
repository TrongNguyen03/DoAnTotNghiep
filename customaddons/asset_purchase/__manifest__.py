# -*- coding: utf-8 -*-
{
    'name': 'Asset Purchase',
    'version': '1.0',
    'summary': 'Manage asset purchase requests and orders, synchronize to assets',
    'category': 'Shopping',
    'author': 'TrongNguyen',
    'depends': ['asset_core','base', 'hr'],
    'data': [
    'security/ir.model.access.csv',
    'views/asset_purchase_menu.xml',
    'views/asset_purchase_request_views.xml',
    'views/asset_purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
}