from odoo import fields, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    property_format_file_report = fields.Selection(
        selection=[
            ('pdf', 'PDF'),
            ('docx', 'DOCX'),
        ],
        string="Format File Report",
        default='pdf',
    )
