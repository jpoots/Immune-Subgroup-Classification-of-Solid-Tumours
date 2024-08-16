class BadRequest(Exception):
    """
    A custom bad request error needed by celery
    Properties:
        status_code: the status code of the object. Defaults to 400
        headers: the object headers
        body: the description of the error
    """

    def __init__(self, status_code=400, headers="Bad Request", body="Bad request sent"):
        self.status_code = status_code
        self.headers = headers
        self.body = body

        super(BadRequest, self).__init__(status_code, headers, body)
