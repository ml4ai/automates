from flask import request
from flask_restplus import Resource

from ..util.dto import PdfProcessDto
from ..service.process.pdf_service import handle_upload, handle_arxiv_id

api = PdfProcessDto.api

@api.route('/upload')
class PdfUploadProcess(Resource):

    @api.response(200, 'Pdf successfully processed.')
    @api.doc('Process an uploaded pdf')
    def post(self):
        return handle_upload(request)


@api.route('/arxiv')
# @api.param('pdf_id', 'The arxiv pdf identifier')
class ArxivPdfProcess(Resource):

    @api.doc('Process a pdf from arxiv')
    def get(self):
        return handle_arxiv_id(request)
