{
    'name': 'Asset Maintenance',
    'version': '1.0.0',
    'summary': 'Maintenance requests and repair flow for company assets',
    'category': 'Operations/Assets',
    'author': 'TrongNguyen',
    'license': 'LGPL-3',
    'depends': ['asset_core', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/maintenance_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
