# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class AssetMaintenance(models.Model):
    _name = 'asset.maintenance'
    _description = 'Asset Maintenance Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'request_date desc'

    name = fields.Char(string='Tiêu đề yêu cầu', required=True, tracking=True)
    asset_id = fields.Many2one(
        'asset.asset',
        string='Tài sản',
        required=True,
        tracking=True,
        domain=[('state', '!=', 'broken')],
        ondelete = 'cascade'
    )
    request_date = fields.Datetime(string='Ngày gửi yêu cầu', default=fields.Datetime.now, tracking=True)
    requested_by = fields.Many2one('res.users', string='Người gửi yêu cầu', default=lambda self: self.env.user,
                                   tracking=True)
    description = fields.Text(string='Mô tả vấn đề')

    state = fields.Selection([
        ('draft', 'Đang chờ'),
        ('in_progress', 'Đang sửa'),
        ('done', 'Đã hoàn tất'),
        ('scrap', 'Hỏng'),
    ], string='Trạng thái', default='draft', tracking=True)

    repair_note = fields.Text(string='Ghi chú sửa chữa')
    completed_date = fields.Datetime(string='Ngày hoàn tất')


    @api.onchange('requested_by')
    def _onchange_requested_by_set_asset_domain(self):
        """
        Khi người yêu cầu thay đổi, giới hạn domain của asset_id:
        - asset.employee_id == employee của requested_by
        - OR asset.department_id == department của employee của requested_by
        - Loại bỏ asset hỏng (state != broken)
        """
        user = self.requested_by or self.env.user
        emp = user.employee_id if user else False
        if emp:
            dept = emp.department_id
            if dept:
                domain = ['&', ('state', '!=', 'broken'), '|',
                          ('employee_id', '=', emp.id),
                          ('department_id', '=', dept.id)]
            else:
                domain = [('employee_id', '=', emp.id), ('state', '!=', 'broken')]
            return {'domain': {'asset_id': domain}}
        return {'domain': {'asset_id': [('state', '!=', 'broken')]}}


    @api.constrains('asset_id', 'state')
    def _check_only_one_in_progress(self):
        for rec in self:
            if rec.state == 'in_progress' and rec.asset_id:
                exists = self.search_count([
                    ('id', '!=', rec.id),
                    ('asset_id', '=', rec.asset_id.id),
                    ('state', '=', 'in_progress')
                ])
                if exists:
                    raise ValidationError("Một tài sản không thể có nhiều yêu cầu bảo trì đang 'Đang sửa' cùng lúc.")


    @api.model
    def create(self, vals):
        user = self.env.user
        employee = user.employee_id
        if not employee:
            raise ValidationError("Bạn chưa liên kết user với nhân viên. Không thể gửi yêu cầu bảo trì.")

        asset = self.env['asset.asset'].browse(vals.get('asset_id')) if vals.get('asset_id') else None
        if not asset:
            raise ValidationError("Tài sản không tồn tại hoặc chưa được chọn.")

        if asset.state == 'broken':
            raise ValidationError("Tài sản này đã hỏng. Không thể gửi yêu cầu bảo trì.")

        # --- QUYỀN ---
        if asset.employee_id:
            # Nếu tài sản phân bổ trực tiếp cho 1 nhân viên
            if asset.employee_id.id != employee.id:
                raise ValidationError("Bạn không có quyền gửi yêu cầu bảo trì cho tài sản này (không phải của bạn).")

        elif asset.department_id:
            # Nếu tài sản phân bổ cho phòng ban
            if not employee.department_id or employee.department_id.id != asset.department_id.id:
                raise ValidationError("Bạn không thuộc phòng ban được phân bổ tài sản này.")

        else:
            raise ValidationError(
                "Tài sản này chưa được phân bổ cho nhân viên hoặc phòng ban nào. Không thể gửi bảo trì.")

        # --- Check trùng phiếu in_progress ---
        if vals.get('state') == 'in_progress':
            exists = self.search_count([('asset_id', '=', asset.id), ('state', '=', 'in_progress')])
            if exists:
                raise ValidationError("Đã có yêu cầu bảo trì 'Đang sửa' cho tài sản này.")

        if not vals.get('requested_by'):
            vals['requested_by'] = user.id

        rec = super().create(vals)
        rec.message_post(body="Phiếu yêu cầu được tạo bởi %s" % (user.name))
        return rec


    def action_start(self):
        for rec in self:
            if rec.asset_id:
                other = self.search([('id', '!=', rec.id), ('asset_id', '=', rec.asset_id.id), ('state', '=', 'in_progress')], limit=1)
                if other:
                    raise ValidationError("Đã có yêu cầu khác đang 'Đang sửa' cho tài sản này. Không thể bắt đầu sửa.")
            rec.state = 'in_progress'
            if rec.asset_id:
                rec.asset_id.with_context(asset_sync_skip=True).write({'state': 'maintenance'})
            rec.message_post(body="Bắt đầu sửa bởi %s" % (self.env.user.name))

    def action_done(self):
        for rec in self:
            rec.state = 'done'
            rec.completed_date = fields.Datetime.now()
            if rec.asset_id:
                active_alloc = self.env['asset.allocation'].search([('asset_id', '=', rec.asset_id.id), ('active', '=', True)], limit=1)
                new_state = 'in_use' if active_alloc else 'stock'
                rec.asset_id.with_context(asset_sync_skip=True).write({'state': new_state})
            rec.message_post(body="Hoàn tất sửa chữa bởi %s" % (self.env.user.name))

    def action_scrap(self):
        for rec in self:
            rec.state = 'scrap'
            rec.completed_date = fields.Datetime.now()
            if rec.asset_id:
                ctx = dict(self.env.context, asset_sync_skip=True)
                rec.asset_id.with_context(ctx).write({'state': 'broken'})
                self.env['asset.allocation'].search([('asset_id', '=', rec.asset_id.id), ('active', '=', True)]) \
                    .with_context(ctx).write({'active': False, 'date_to': fields.Date.context_today(self)})
            rec.message_post(body="Đánh dấu hỏng/thanh lý bởi %s" % (self.env.user.name))
