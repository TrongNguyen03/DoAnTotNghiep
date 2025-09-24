# -*- coding: utf-8 -*-
{
    'name': 'custom views',
    'version': '1.0.0',
    'summary': 'điều chỉnh 1 số views gốc của odoo',
    'depends': ['web','hr'],
    'data': [
        'security/asset_groups.xml',
        'views/hide_login.xml',
        'views/custom_my_profile.xml',
        'views/custom_hr_profile.xml',
        'views/hide_menu_app.xml',
    ],
    'assets': {
        'web.assets_backend': [
           'custom_views/static/src/scss/hide_menu.scss',
            'custom_views/static/src/js/title.js',
        ],
        'web.assets_frontend': [
            'custom_views/static/src/scss/custom_login.scss',
    ],

    },
    'installable': True,
    'application': False,
}
