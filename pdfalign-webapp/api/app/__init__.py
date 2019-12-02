from flask_restplus import Api
from flask import Blueprint

from .main.controller.process_server import api as process_ns
from .main.controller.annotation_server import api as annotation_ns

blueprint = Blueprint('api', __name__)

api = Api(blueprint,
          title='FLASK RESTPLUS API BOILER-PLATE WITH JWT',
          version='1.0',
          description='a boilerplate for flask restplus web service'
          )
api.add_namespace(process_ns, path='/process')
api.add_namespace(annotation_ns, path='/annotation')
