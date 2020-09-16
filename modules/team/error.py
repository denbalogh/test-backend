from error import APIException

class CoachMemberConflictError(APIException):
    def __init__(self):
        super(CoachMemberConflictError, self).__init__(status_code=409, error_code=1301, message="A coach cannot be member of a team")
