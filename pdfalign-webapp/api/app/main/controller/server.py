from flask import request
from flask_restplus import Resource

from ..util.dto import PdfProcessDto
from ..service.pdf_service import handle_upload, handle_arxiv_id

api = PdfProcessDto.api


@api.route('/upload')
class PdfUploadProcess(Resource):

    @api.response(200, 'Pdf successfully processed.')
    @api.doc('Process an uploaded pdf')
    # @api.expect(_user, validate=True)
    def post(self):
        return handle_upload(request)


@api.route('/arxiv/<pdf_id>')
@api.param('public_id', 'The arxiv pdf identifier')
# @api.response(404, 'User not found.')
class ArxivPdfProcess(Resource):

    @api.doc('Process a pdf from arxiv')
    # @api.marshal_with(_user)
    def post(self, pdf_id):
        return handle_arxiv_id(pdf_id)
