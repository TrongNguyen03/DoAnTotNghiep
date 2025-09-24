
from odoo import http
from odoo.http import request

class TabTitleController(http.Controller):
    @http.route('/get/tab/title/', type='http', auth='user', csrf=False)
    def get_tab_title(self):
        return request.make_response(
            "Cty TNHH NQT",
            headers=[('Content-Type', 'text/plain')]
        )
