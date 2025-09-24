import os
import PyPDF2
import io
import tempfile
import json
from pdf2docx import Converter

from odoo.addons.web.controllers.report import ReportController
from odoo.http import request, route, content_disposition
from odoo.tools.safe_eval import safe_eval, time


def pdf2word(data, filename):
    pdf_reader = PyPDF2.PdfFileReader(io.BytesIO(data))
    pdf_writer = PyPDF2.PdfFileWriter()
    for page_num in range(pdf_reader.numPages):
        page = pdf_reader.getPage(page_num)
        pdf_writer.addPage(page)
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, 'wb') as tmp:
            pdf_writer.write(tmp)
        cv = Converter(path)
        cv.convert(path)
        with open(path, 'rb') as f:
            text = f.read()
            response = request.make_response(text, headers=[('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')])
            response.headers.add('Content-Disposition', content_disposition(filename))
        return response
    finally:
        pass


class ReportControllerExt(ReportController):

    @route(['/report/download'], type='http', auth="user")
    def report_download(self, data, context=None):
        res = super(ReportControllerExt, self).report_download(data, context)
        requestcontent = json.loads(data)
        url, type = requestcontent[0], requestcontent[1]
        if type == 'qweb-pdf':
            converter = 'pdf' if type == 'qweb-pdf' else 'text'
            extension = 'pdf' if type == 'qweb-pdf' else 'txt'

            pattern = '/report/pdf/' if type == 'qweb-pdf' else '/report/text/'
            reportname = url.split(pattern)[1].split('?')[0]

            docids = None
            if '/' in reportname:
                reportname, docids = reportname.split('/')

            if docids:
                response = self.report_routes(reportname, docids=docids, converter=converter, context=context)
            else:
                data = dict(url_decode(url.split('?')[1]).items())  # decoding the args represented in JSON
                if 'context' in data:
                    context, data_context = json.loads(context or '{}'), json.loads(data.pop('context'))
                    context = json.dumps({**context, **data_context})
                response = self.report_routes(reportname, converter=converter, context=context, **data)

            report = request.env['ir.actions.report']._get_report_from_name(reportname)
            filename = "%s.%s" % (report.name, extension)
            if docids:
                ids = [int(x) for x in docids.split(",")]
                obj = request.env[report.model].browse(ids)
                if report.print_report_name and not len(obj) > 1:
                    report_name = safe_eval(report.print_report_name, {'object': obj, 'time': time})
                    filename = "%s.%s" % (report_name, extension)
            if report.property_format_file_report == 'docx':
                filename = filename.replace('.pdf', '.docx')
                return pdf2word(res.data, filename)
        return res
