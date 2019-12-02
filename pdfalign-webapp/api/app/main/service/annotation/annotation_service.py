import json
from flask import jsonify
from app.main.model.annotation import Annotation
from app.main import db

def handle_store(request):
    data = request.json

    annotation_json = data['annotation_data']
    try:
        json.loads(annotation_json)
    except:
        return jsonify({'status_code' : 404,
            'message' : 'Unable to parse json annotation json data'
        })

    # If id is -1, create a new annotation
    if data['annotation_id'] == -1:
        annotation = Annotation(equation_aabb=data['equation_aabb'],
            annotation_json=annotation_json)
    else:
        # Check if the annotation exists, throw an error if it doesnt
        if not retrieve_annotation(data['annotation_id']):
            return jsonify({'status_code' : 404,
                'message' : 'Unknown annotation id\'' + \
                    data['annotation_id'] + '\''
                })

        # Update existing annotation
        annotation = Annotation(id=data['annotation_id'],
            equation_aabb=data['equation_aabb'],
            annotation_json=annotation_json)

    upsert(annotation)

    response_object = {
        'status': 'success',
        'status_code' : 201,
        'message': 'Successfully stored.'
    }
    return response_object

def handle_get(request):
    id = pdf_id = request.args.get('id')
    if not id:
        return jsonify({'message' : 'No id query parameter given'})

    annotation = retrieve_annotation(id)
    if not annotation:
        return jsonify({'status_code' : 404,
            'message' : 'Unknown annotation id \'' + id + '\''
        })
    return jsonify({'annotation_id' : annotation.id,
        'annotation_data' : annotation.annotation_json,
        'equation_aabb' : annotation.equation_aabb
    })

def retrieve_annotation(id):
    return Annotation.query.filter_by(id=id).first()


def upsert(data):
    db.session.merge(data)
    db.session.commit()
