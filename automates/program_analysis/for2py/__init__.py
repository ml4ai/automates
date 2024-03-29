import os
from pathlib import Path

os.environ["CLASSPATH"] = str(Path(__file__).parent / "bin" / "*")


class For2PyError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)

        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = f"For2Py error: {self.message}"
        return rv
