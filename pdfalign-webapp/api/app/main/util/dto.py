from flask_restplus import Namespace, fields


class PdfProcessDto:
    api = Namespace('process', description='pdf process related operations')

class AnnotationDto:
    api = Namespace('annotation', description='handle storing and retrieving' +
        ' paper annotations')
    annotation = api.model('annotation', {
        'annotation_id': fields.Integer(required=True, allow_null=True,
            description='annotation unique id'),
        'annotation_data': fields.String(required=True,
            description='json representing annotations'),
        'equation_aabb': fields.String(required=True,
            description='String representing aabb box for equation being ' \
                + 'annotated')
        # Other data,
    })
