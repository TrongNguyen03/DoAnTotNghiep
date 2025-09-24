{
    'name': "Report Print Docx",

    'summary': """
        This module provide features with report in odoo.
    """,

    'description': """
What it does
============
* This module provide features with report in odoo.

Features
========
1. Convert report to PDF or DOCX file.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,

    'author': "Hieu Hoang",
    'support': "hieu.hoang121199@gmail.com",
    'category': 'Printer',
    'version': '0.1.0',
    'depends': ['web'],
    'data': [
        'views/ir_actions_report_views.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}

