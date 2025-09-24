# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AssetPurchaseRequestLine(models.Model):
    _name = 'asset.purchase.request.line'
    _description = 'Chi tiết đề xuất mua tài sản'

    request_id = fields.Many2one(
        'asset.purchase.request',
        string='Phiếu đề xuất',
        ondelete='cascade',
        required=True
    )
    product_name = fields.Char(string='Tên tài sản', required=True)
    category_id = fields.Many2one('asset.category', string='Loại tài sản')
    quantity = fields.Integer(string='Số lượng', default=1)
    unit_price = fields.Integer(string='Đơn giá')
    subtotal = fields.Integer(string='Thành tiền', compute='_compute_subtotal')

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity * rec.unit_price
