# asset_core/__manifest__.py
{
    'name': 'Asset Core',
    'version': '1.0.0',
    'summary': 'Core models for Asset Management (Assets, Categories, Allocations)',
    'category': 'Operations/Inventory',
    'author': 'TrongNguyen',
    'license': 'LGPL-3',
    'depends': ['base', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/asset_views.xml',
        'views/allocation_views.xml',
    ],
    'assets': {
    'web.assets_backend': [
        'asset_core/static/src/scss/show_required.scss',
        'asset_core/static/src/js/asset_list_buttons.js',
        'asset_core/static/src/xml/asset_list_buttons.xml',

    ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
