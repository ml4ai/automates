from werkzeug.utils import secure_filename
from flask import jsonify
from .pdf_transform import PdfAlign
import json
import os

def handle_bytes(pdf_bytes):
    pdf_align = PdfAlign()
    pdf_align.process(pdf_bytes)

    pdf_align_data = { 'aabb_trees' : pdf_align.aabb_trees,
        'annotation_aabb' : pdf_align.annotation_aabb,
        'all_tokens' : pdf_align.all_tokens }

    return json.dumps(pdf_align_data, default=lambda x: x.__dict__)

def handle_arxiv_id(id):
    pass

def handle_upload(request):
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message' : 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file:
        # Not saving file so this should not matter
        # filename = secure_filename(file.filename)
        pdf_align_data = handle_bytes(file.read())
        resp = jsonify({'message' : 'Pdf successfully processed',
            'data' : pdf_align_data})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify({'message' : 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
        resp.status_code = 400
        return resp
