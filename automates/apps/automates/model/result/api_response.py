class ApiResponse():

    code: int
    type: str
    message: str

    def __init__(self, code, type, message):
        self.code = code
        self.type = type
        self.message = message