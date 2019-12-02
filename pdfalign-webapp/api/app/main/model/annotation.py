from .. import db
from sqlalchemy.dialects.postgresql import JSONB

class Annotation(db.Model):
    """ Annotation Model for storing annotation related details """
    __tablename__ = "annotation"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # TODO how should we store annotations? Do we want another table for papers
    # and have a foreign key?
    equation_aabb = db.Column(db.String(), unique=False, nullable=False)
    annotation_json = db.Column(JSONB, unique=False, nullable=False)

    def __repr__(self):
        return "<Annotation '{}'>".format(self.id)
