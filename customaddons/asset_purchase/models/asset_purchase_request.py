# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import uuid


class AssetPurchaseRequest(models.Model):
    _name = 'asset.purchase.request'
    _description = 'Phiếu đề xuất mua tài sản'
    _order = 'create_date desc'

    name = fields.Char(
        string='Mã phiếu',
        required=True,
        copy=False,
        index=True,
        default=lambda self: self._default_name_req()
    )
    requested_by = fields.Many2one(
        'res.users',
        string='Người đề xuất',
        default=lambda self: self.env.user
    )
    approved_by = fields.Many2one(
        'res.users',
        string='Người phê duyệt',
        readonly=True
    )
    date = fields.Date(string='Ngày đề xuất', default=fields.Date.context_today)
    reason = fields.Text(string='Lý do đề xuất')
    state = fields.Selection([
        ('draft', 'Đang chờ'),
        ('approved', 'Đã duyệt'),
        ('cancel', 'Đã hủy'),
        ('converted', 'Đã chuyển thành phiếu mua')
    ], string="Trạng thái", default='draft')

    line_ids = fields.One2many(
        'asset.purchase.request.line',
        'request_id',
        string='Chi tiết đề xuất'
    )

    @api.model
    def create(self, vals):
        if not vals.get('line_ids'):
            raise ValidationError("Cần ít nhất 1 dòng sản phẩm trong phiếu đề xuất.")
        if not vals.get('name'):
            vals['name'] = f"REQ-{str(uuid.uuid4())[:8].upper()}"
        return super().create(vals)

    def _default_name_req(self):
        """Sinh mã mặc định REQ-XXXXXXXX"""
        return f"REQ-{str(uuid.uuid4())[:8].upper()}"

    def action_confirm(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError('Cần ít nhất 1 dòng chi tiết trong phiếu đề xuất.')
            if rec.state != 'draft':
                raise ValidationError('Chỉ phiếu ở trạng thái chờ mới được duyệt.')
            rec.state = 'approved'
            rec.approved_by = self.env.user   # gán người phê duyệt

    def action_cancel(self):
        for rec in self:
            if rec.state in ['approved', 'converted']:
                raise ValidationError("Phiếu đã duyệt hoặc đã chuyển sang phiếu mua, không thể hủy.")
            rec.state = 'cancel'

    def action_to_purchase(self):
        order_obj = self.env['asset.purchase.order']
        created = []
        for req in self:
            if not req.line_ids:
                raise ValidationError("Phiếu đề xuất phải có ít nhất 1 sản phẩm mới được chuyển thành phiếu mua.")
            if req.state == 'converted':
                raise ValidationError(f"Phiếu đề xuất {req.name} đã được chuyển thành phiếu mua rồi.")

            vals = {
                'origin_request_id': req.id,
                'requested_by': req.requested_by.id,
                'date': req.date,
                'line_ids': [(0, 0, {
                    'product_name': l.product_name,
                    'category_id': l.category_id.id,
                    'quantity': l.quantity,
                    'unit_price': l.unit_price,
                }) for l in req.line_ids]
            }
            order = order_obj.create(vals)
            req.state = 'converted'
            created.append(order)
        return created
