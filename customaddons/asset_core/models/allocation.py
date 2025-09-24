# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta, date


class AssetAllocation(models.Model):
    _name = 'asset.allocation'
    _description = 'Asset Allocation (history)'
    _order = 'date_from desc'

    asset_id = fields.Many2one(
        'asset.asset',
        string='Tài sản',
        required=True,
        ondelete='cascade',
    )

    allocation_type = fields.Selection([
        ('employee', 'Phân cho nhân viên'),
        ('department', 'Phân cho phòng ban'),
    ], string='Loại phân bổ', required=True, default='employee')

    employee_id = fields.Many2one('hr.employee', string='Nhân viên được phân bổ')
    department_id = fields.Many2one('hr.department', string='Phòng ban được phân bổ')
    date_from = fields.Date(string='Ngày bắt đầu', required=True, default=fields.Date.context_today)
    date_to = fields.Date(string='Ngày kết thúc')
    active = fields.Boolean(string='Kích hoạt', default=True)
    note = fields.Text(string='Ghi chú')


    @api.model
    def _get_available_assets_domain(self):
        allocated_asset_ids = self.env['asset.allocation'].search([
            ('active', '=', True)
        ]).mapped('asset_id').ids
        return [
            ('id', 'not in', allocated_asset_ids),
            ('state', '!=', 'broken')
        ]

    @api.onchange('asset_id')
    def _onchange_asset_id_domain(self):
        allocated_asset_ids = self.env['asset.allocation'].search([
            ('active', '=', True)
        ]).mapped('asset_id').ids
        return {
            'domain': {
                'asset_id': [
                    ('id', 'not in', allocated_asset_ids),
                    ('state', '!=', 'broken')
                ]
            }
        }

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for rec in self:
            if rec.employee_id:
                rec.department_id = rec.employee_id.department_id.id
            else:
                rec.department_id = False


    @api.constrains('employee_id', 'department_id')
    def _check_employee_or_department(self):
        for rec in self:
            if not rec.employee_id and not rec.department_id:
                raise ValidationError("Bạn phải chọn Nhân viên hoặc Phòng ban cho phân bổ.")

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for rec in self:
            if rec.date_to and rec.date_from and rec.date_to < rec.date_from:
                raise ValidationError('Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu.')


    def _close_previous_allocations(self):
        for rec in self:
            if not rec.asset_id or not rec.active:
                continue
            others = self.search([
                ('asset_id', '=', rec.asset_id.id),
                ('id', '!=', rec.id),
                ('active', '=', True)
            ])
            for o in others:
                prev_day = fields.Date.from_string(str(rec.date_from)) - timedelta(days=1)
                o.with_context(asset_sync_skip=True).write({
                    'active': False,
                    'date_to': prev_day
                })


    @api.model
    def create(self, vals):
        rec = super().create(vals)
        if rec.active:
            rec._close_previous_allocations()

        # nếu hết hạn thì tự inactive
        if rec.date_to and rec.date_to < date.today():
            rec.write({'active': False})

        rec._sync_asset_from_current_alloc()
        return rec


    def _sync_asset_from_current_alloc(self):
        for rec in self:
            if not rec.asset_id or self.env.context.get('asset_sync_skip'):
                continue

            ctx = dict(self.env.context, asset_sync_skip=True)
            today = fields.Date.context_today(self)

            active_alloc = self.search([
                ('asset_id', '=', rec.asset_id.id),
                ('active', '=', True),
                '|',
                ('date_to', '=', False),
                ('date_to', '>=', today),
            ], limit=1, order="date_from desc")

            if active_alloc:
                values = {
                    'allocation_type': active_alloc.allocation_type,
                    'employee_id': False,
                    'department_id': False,
                    'state': 'in_use'
                }
                if active_alloc.allocation_type == 'employee':
                    values['employee_id'] = active_alloc.employee_id.id if active_alloc.employee_id else False
                    values['department_id'] = (
                        active_alloc.department_id.id if active_alloc.department_id
                        else active_alloc.employee_id.department_id.id if active_alloc.employee_id and active_alloc.employee_id.department_id
                        else False
                    )
                    if not values['employee_id'] and not values['department_id']:
                        values['state'] = 'stock'
                else:
                    values['department_id'] = active_alloc.department_id.id if active_alloc.department_id else False

                rec.asset_id.with_context(ctx).write(values)
            else:
                rec.asset_id.with_context(ctx).write({
                    'employee_id': False,
                    'department_id': False,
                    'state': 'stock'
                })


    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.active:
                # nếu hết hạn thì inactive
                if rec.date_to and rec.date_to < date.today():
                    rec.write({'active': False})
                else:
                    rec._close_previous_allocations()
        self._sync_asset_from_current_alloc()
        return res


    def action_return_to_stock(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.write({'active': False, 'date_to': today})
            if rec.asset_id and not self.env.context.get('asset_sync_skip'):
                ctx = dict(self.env.context, asset_sync_skip=True)
                other = self.search([('asset_id', '=', rec.asset_id.id), ('active', '=', True)], limit=1)
                if other:
                    other.with_context(ctx)._sync_asset_from_current_alloc()
                else:
                    rec.asset_id.with_context(ctx).write({
                        'employee_id': False,
                        'department_id': False,
                        'state': 'stock'
                    })


    @api.model
    def cron_auto_close_expired_allocations(self):
        today = fields.Date.context_today(self)
        expired_allocs = self.search([
            ('active', '=', True),
            ('date_to', '!=', False),
            ('date_to', '<', today),
        ])
        for alloc in expired_allocs:
            alloc.write({'active': False})
        if expired_allocs:
            expired_allocs._sync_asset_from_current_alloc()
