# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import uuid


class AssetPurchaseOrder(models.Model):
    _name = 'asset.purchase.order'
    _description = 'Phiếu mua tài sản'
    _order = 'create_date desc'

    name = fields.Char(
        string='Mã phiếu',
        required=True,
        copy=False,
        index=True,
        default=lambda self: self._default_name_order()
    )
    origin_request_id = fields.Many2one('asset.purchase.request', string='Từ phiếu đề xuất', domain="[('state', '=', 'approved')]")
    requested_by = fields.Many2one('res.users', string='Người đề xuất', default=lambda self: self.env.user)
    date = fields.Date(string='Ngày mua', default=fields.Date.context_today)
    state = fields.Selection([
        ('draft', 'Đang chờ'),
        ('confirmed', 'Đã xác nhận'),
        ('to_receive', 'Chờ nhận hàng'),
        ('done', 'Hoàn thành'),
        ('cancel', 'Đã hủy')
    ], string="Trạng thái", default='draft')

    line_ids = fields.One2many(
        'asset.purchase.order.line',
        'order_id',
        string='Chi tiết phiếu mua'
    )

    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)

    total_amount = fields.Integer(string='Tổng tiền', compute='_compute_total')


    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = f"PO-{str(uuid.uuid4())[:8].upper()}"
        if not vals.get('line_ids'):
            raise ValidationError("Cần ít nhất 1 dòng sản phẩm để tạo phiếu mua.")
        if vals.get('origin_request_id'):
            req = self.env['asset.purchase.request'].browse(vals['origin_request_id'])
            if req.state == 'converted':
                raise ValidationError(f"Phiếu đề xuất {req.name} đã được tạo phiếu mua, không thể dùng lại.")

            # Khi tạo phiếu mua thành công thì cập nhật trạng thái phiếu đề xuất
            req.state = 'converted'
        return super().create(vals)

    def _default_name_order(self):
        return f"PO-{str(uuid.uuid4())[:8].upper()}"

    def _compute_total(self):
        for rec in self:
            rec.total_amount = sum(rec.line_ids.mapped('subtotal'))

    def action_confirm(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError('Cần ít nhất 1 dòng chi tiết mua hàng.')
            rec.state = 'confirmed'

    def action_mark_to_receive(self):
        for rec in self:
            rec.state = 'to_receive'

    def action_mark_done(self):
        """Khi mua hàng hoàn tất: tạo bản ghi tài sản (asset.asset) ở trạng thái 'Trong kho'."""
        Asset = self.env['asset.asset']
        created_assets = self.env['asset.asset']
        for rec in self:
            if rec.state == 'done':
                continue
            if not rec.line_ids:
                raise ValidationError("Không thể hoàn tất phiếu mua không có sản phẩm.")
            for line in rec.line_ids:
                for i in range(max(0, int(line.quantity))):
                    vals = {
                        'name': line.product_name,
                        'category_id': line.category_id.id or False,
                        'code': str(uuid.uuid4())[:8].upper(),
                        'state': 'stock',
                        'purchase_value': line.unit_price,
                        'purchase_date': rec.date,
                    }
                    asset = Asset.create(vals)
                    created_assets += asset
            rec.state = 'done'
        return created_assets

    def action_cancel(self):
        for rec in self:
            if rec.state in ['confirmed','done','to_receive' ]:
                raise ValidationError("Phiếu đã xác nhận, không thể hủy.")
            rec.state = 'cancel'
