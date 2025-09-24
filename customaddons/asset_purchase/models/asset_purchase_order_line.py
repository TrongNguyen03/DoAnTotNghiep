# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AssetPurchaseOrderLine(models.Model):
    _name = 'asset.purchase.order.line'
    _description = 'Chi tiết phiếu mua tài sản'

    order_id = fields.Many2one(
        'asset.purchase.order',
        string='Phiếu mua',
        ondelete='cascade',
        required=True
    )
    product_name = fields.Char(string='Tên tài sản', required=True)
    category_id = fields.Many2one('asset.category', string='Loại tài sản')
    quantity = fields.Integer(string='Số lượng', default=1)
    unit_price = fields.Integer(string='Đơn giá')
    subtotal = fields.Integer(string='Thành tiền', compute='_compute_subtotal')

    asset_ids = fields.One2many(
        'asset.asset',
        'id',
        string='Tài sản được tạo',
        help='Các tài sản được tạo từ dòng này'
    )

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity * rec.unit_price
