""" Handling of occurring errors

This module defines various exceptions that can occur during execution.
"""

import util

class APIException(Exception):
    def __init__(self, message=None, status_code=500, error_code=1000):
        Exception.__init__(self, message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code

    def getResponse(self):
        return util.response(status_code=self.status_code, error_code=self.error_code, error_message=self.message)

class NotFoundError(APIException):
    def __init__(self):
        super(NotFoundError, self).__init__(status_code=404, error_code=1001, message="The requested ressource was not found")

class NoJsonPayloadException(APIException):
    def __init__(self):
        super(NoJsonPayloadException, self).__init__(status_code=400, error_code=1002, message="No JSON data in message body")

class MalformedPayloadException(APIException):
    def __init__(self, description):
        super(MalformedPayloadException, self).__init__(status_code=400, error_code=1003, message="The JSON payload was malformed: " + description)

class BadParameterError(APIException):
    def __init__(self, description):
        super(BadParameterError, self).__init__(status_code=400, error_code=1005, message="Bad Parameter: " + description)

class MethodNotAllowedError(APIException):
    def __init__(self):
        super(MethodNotAllowedError, self).__init__(status_code=405, error_code=1004, message="Method not allowed in this context.")

class InvalidRequestHeader(APIException):
    def __init__(self, description=None):
        if description:
            super(InvalidRequestHeader, self).__init__(status_code=400, error_code=1006, message="The request header contains invalid or contradicting fields or values: " + description)
        else:
            super(InvalidRequestHeader, self).__init__(status_code=400, error_code=1006, message="The request header contains invalid or contradicting fields or values.")


class NoAuthorizationHeaderError(APIException):
    def __init__(self):
        super(NoAuthorizationHeaderError, self).__init__(status_code=401, error_code=1101, message="No authorization header")

class SessionExpiredError(APIException):
    def __init__(self):
        super(SessionExpiredError, self).__init__(status_code=401, error_code=1102, message="Your session has expired")

class InvalidSessionError(APIException):
    def __init__(self):
        super(InvalidSessionError, self).__init__(status_code=401, error_code=1103, message="The session token provided is invalid")

class ClientOriginViolation(APIException):
    def __init__(self):
        super(ClientOriginViolation, self).__init__(status_code=403, error_code=1104, message="The request was sent from a new IP address, please login again")

class AccessDeniedError(APIException):
    def __init__(self):
        super(AccessDeniedError, self).__init__(status_code=403, error_code=1105, message="The access to this function is not allowed for the logged in user")

class InvalidAuthorizationHeader(APIException):
    def __init__(self):
        super(InvalidAuthorizationHeader, self).__init__(status_code=403, error_code=1106, message="The authorization header is invalid")
