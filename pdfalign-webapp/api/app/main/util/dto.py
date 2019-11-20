from flask_restplus import Namespace, fields


class PdfProcessDto:
    api = Namespace('process', description='pdf process related operations')
    # user = api.model('user', {
    #     'email': fields.String(required=True, description='user email address'),
    #     'username': fields.String(required=True, description='user username'),
    #     'password': fields.String(required=True, description='user password'),
    #     'public_id': fields.String(description='user Identifier')
    # })
