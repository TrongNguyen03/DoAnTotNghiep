# -*- coding: utf-8 -*-
from odoo import models, fields, api
import uuid
from odoo.exceptions import ValidationError


class AssetCategory(models.Model):
    _name = 'asset.category'
    _description = 'Asset Category'
    _order = 'name'

    name = fields.Char(string='Category Name', required=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')


class Asset(models.Model):
    _name = 'asset.asset'
    _description = 'Company Asset'
    _order = 'create_date desc'

    name = fields.Char(string='Tên tài sản', required=True)
    code = fields.Char(
        string='Mã tài sản',
        copy=False,
        index=True,
        default=lambda self: self._default_code()
    )
    serial_number = fields.Char(string='Số sê-ri')
    category_id = fields.Many2one('asset.category', string='Loại tài sản')

    allocation_type = fields.Selection([
        ('employee', 'Phân cho nhân viên'),
        ('department', 'Phân cho phòng ban'),
    ], string='Loại phân bổ', required=True, default='employee')
    employee_id = fields.Many2one('hr.employee', string='Nhân viên được phân bổ')
    department_id = fields.Many2one('hr.department', string='Phòng ban được phân bổ')
    purchase_date = fields.Date(string='Ngày mua')
    purchase_value = fields.Integer(string='Giá mua')
    warranty_end_date = fields.Date(string='Ngày hết bảo hành')
    image_1920 = fields.Image("Ảnh")

    state = fields.Selection([
        ('stock', 'Trong kho'),
        ('in_use', 'Đang sử dụng'),
        ('maintenance', 'Đang bảo trì'),
        ('broken', 'Hỏng'),
    ], string='Trạng thái', default='stock', readonly=True, copy=False)

    note = fields.Text(string='Ghi chú')

    allocation_count = fields.Integer(string='Số lần phân bổ', compute='_compute_allocation_count')
    maintenance_count = fields.Integer(string='Số phiếu bảo trì', compute='_compute_maintenance_count')


    def _compute_allocation_count(self):
        for rec in self:
            rec.allocation_count = self.env['asset.allocation'].search_count([('asset_id', '=', rec.id)])

    def _compute_maintenance_count(self):
        for rec in self:
            rec.maintenance_count = self.env['asset.maintenance'].search_count([('asset_id', '=', rec.id)])

    def _default_code(self):
        """Sinh mã tài sản mặc định: 8 ký tự ngẫu nhiên"""
        return str(uuid.uuid4())[:8].upper()

    def action_open_import_wizard(self):
        return {
            "name": "Import Tài sản",
            "type": "ir.actions.act_window",
            "res_model": "asset.import.wizard",
            "view_mode": "form",
            "target": "new",
        }


    @api.constrains('serial_number', 'code')
    def _check_unique_sn_code(self):
        for rec in self:
            if rec.serial_number:
                domain = [('serial_number', '=', rec.serial_number)]
                if rec.id:
                    domain.append(('id', '!=', rec.id))
                if self.search_count(domain):
                    raise ValidationError('Số sê-ri phải là duy nhất.')
            if rec.code:
                domain = [('code', '=', rec.code)]
                if rec.id:
                    domain.append(('id', '!=', rec.id))
                if self.search_count(domain):
                    raise ValidationError('Mã tài sản phải là duy nhất.')


    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = str(uuid.uuid4())[:8].upper()
        rec = super().create(vals)

        # Nếu có thông tin phân bổ trong asset thì sinh phiếu allocation
        if rec.employee_id or rec.department_id:
            self.env['asset.allocation'].create({
                'asset_id': rec.id,
                'allocation_type': rec.allocation_type,
                'employee_id': rec.employee_id.id if rec.employee_id else False,
                'department_id': rec.department_id.id if rec.department_id else False,
                'date_from': fields.Date.context_today(self),
                'note': 'Sinh tự động khi import Excel',
            })

        return rec

    # Name Get
    def name_get(self):
        result = []
        for rec in self:
            name = f"[{rec.code}] {rec.name}"
            result.append((rec.id, name))
        return result

    # delete
    def unlink(self):
        locked_states = ['stock','in_use', 'maintenance']
        for rec in self:
            if rec.state in locked_states:
                raise ValidationError("Không thể xóa tài sản khi đang ở trạng thái trong kho/sử dụng/bảo trì.")
        return super().unlink()
