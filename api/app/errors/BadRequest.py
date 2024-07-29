class BadRequest(Exception):

    def __init__(self, status_code=400, headers="Bad Request", body="Bad request sent"):
        self.status_code = status_code
        self.headers = headers
        self.body = body

        super(BadRequest, self).__init__(status_code, headers, body)
