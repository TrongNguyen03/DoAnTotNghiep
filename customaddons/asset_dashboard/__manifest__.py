# -*- coding: utf-8 -*-
{
    'name': 'Asset Dashboard & Reports',
    'version': '1.0.0',
    'summary': 'Dashboard & Reports for Company Assets',
    'category': 'Operations/Inventory',
    'author': 'TrongNguyen',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'hr', 'asset_core'],
    'data': [
        'security/ir.model.access.csv',
        'views/asset_dashboard_views.xml',
    ],

    'installable': True,
    'application': True,
}
