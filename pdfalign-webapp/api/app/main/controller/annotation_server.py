from flask import request
from flask_restplus import Resource

from ..util.dto import AnnotationDto
from ..service.annotation.annotation_service import handle_store, handle_get

api = AnnotationDto.api
_annotation = AnnotationDto.annotation


@api.route('/')
class StoreAnnotation(Resource):

    @api.response(200, 'Annotation successfully stored')
    @api.doc('Store an annotation')
    @api.expect(_annotation, validate=True)
    def post(self):
        return handle_store(request)

    @api.doc('Retrieve annotation data')
    @api.response(404, 'Annotation not found.')
    @api.param('id', 'The unique annotation id')
    def get(self):
        return handle_get(request)
