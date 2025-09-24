from odoo import models, fields

class AssetReport(models.Model):
    _name = 'asset.report'
    _description = 'Asset Reports'
    _auto = False

    name = fields.Char(string='Tên tài sản', readonly=True)
    category_id = fields.Many2one('asset.category', string='Nhóm tài sản', readonly=True)
    year = fields.Char(string='Năm', readonly=True)

    # Số liệu tài sản
    asset_count = fields.Integer(string='Số lượng tài sản', readonly=True)
    total_purchase = fields.Integer(string='Tổng giá trị mua', readonly=True)

    # Nhân viên
    employee_count = fields.Integer(string='Số nhân viên sử dụng', readonly=True)
    allocation_count = fields.Integer(string='Số lần phân bổ', readonly=True)
    allocation_avg = fields.Integer(string='Phân bổ TB / tài sản', readonly=True)

    # Tình trạng
    broken_count = fields.Integer(string='Số hỏng', readonly=True)
    broken_ratio = fields.Integer(string='Tỷ lệ hỏng (%)', readonly=True)

    def init(self):
        self.env.cr.execute("""
            DROP VIEW IF EXISTS asset_report;
            CREATE OR REPLACE VIEW asset_report AS (
                SELECT
                    MIN(a.id) AS id, -- cần MIN/ MAX để làm primary key
                    a.name AS name,
                    a.category_id AS category_id,
                    EXTRACT(YEAR FROM a.purchase_date)::text AS year,

                    -- Tài sản
                    COUNT(a.id)::int AS asset_count,
                    SUM(a.purchase_value)::int AS total_purchase,

                    -- Nhân viên
                    COUNT(DISTINCT al.employee_id)::int AS employee_count,
                    COUNT(al.id)::int AS allocation_count,
                    (CASE WHEN COUNT(DISTINCT a.id) > 0
                          THEN ROUND(COUNT(al.id)::numeric / COUNT(DISTINCT a.id))
                          ELSE 0 END)::int AS allocation_avg,

                    -- Tình trạng
                    SUM(CASE WHEN a.state='broken' THEN 1 ELSE 0 END)::int AS broken_count,
                    (CASE WHEN COUNT(a.id) > 0
                          THEN ROUND(SUM(CASE WHEN a.state='broken' THEN 1 ELSE 0 END) * 100.0 / COUNT(a.id))
                          ELSE 0 END)::int AS broken_ratio

                FROM asset_asset a
                LEFT JOIN asset_allocation al ON al.asset_id = a.id
                GROUP BY a.name, a.category_id, year
            )
        """)
