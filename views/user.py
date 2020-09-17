"""User routes

Blueprint defining routes for user and session management.
"""

import json
import datetime

from flask import Blueprint, g, request

from util import auth
from modules.user import controller
from modules.team import controller as team_controller
from util.auth import noauth, restrict_to, authenticate
from error import APIException, NotFoundError, BadParameterError, AccessDeniedError
from model.User import User
from model.Roles import SystemRole
from util import response, validate, hash_password
from util.structs import UserInputDict

user = Blueprint("user", __name__)
TRIAL_PERIOD = 7

def check_trial(user):
    # Check for trial period
    if user.trial_period_expire_date is not None and user.trial_period_expire_date < datetime.datetime.now():
        raise TrialPeriodExpiredError()

@user.route("/info", methods=["GET"])
def getUserInfo():
    user_id = g.session["userID"]

    u = controller.get_user_by_id(user_id)
    
    # Check for trial period
    check_trial(u)
    
    payload = {
        "id"   : str(u.id)
    }

    if u.mail:
        payload["mail"] = u.mail

    if u.name is not None:
        payload["name"] = u.name
        
    if u.trial_period_expire_date is not None:
        payload["trial_period_expire_date"] = u.trial_period_expire_date

    session = {}
    if g.session["userRole"] != "coach":
        args = UserInputDict(request.args)
        expand = args.get_list("expand", [])

        team = g.session["team"]
        if "team" in expand:
            team = team_controller.get_team_by_id(g.session["team"]).to_response()

        session = {
            "team": team,
            "role": "member"
        }

    else:
        session["role"] = "coach"

    payload["session"] = session
    
    return response(payload=payload)

@user.route("/register", methods=["POST"])
@validate("user_registration_req")
def registerUser():
    if _check_password(g.payload["password"]):
        if controller.get_user_by_mail(g.payload["mail"]):
            # Raise error if user is already registered
            raise UsernameTakenError()

        # Register new user
        user_data = {}

        user_data["mail"] = g.payload["mail"]
        user_data["password"] = g.payload["password"]
            
        if "name" in g.payload:
            user_data["name"] = g.payload["name"]

        if "role" in g.payload and g.payload["role"] not in [SystemRole.USER.value, SystemRole.GLOBAL_ADMIN.value]:
            raise APIException(message="This user role cannot be registered using this path at the moment", status_code=403)
        else:
            auth.authenticate(set_session=False, access_limit=[SystemRole.GLOBAL_ADMIN])
            user_data["role"] = SystemRole.USER

        u = controller.create_user(**user_data)

        return response(created=str(u.id))
    else:
        raise InvalidPasswordFormatError()

@user.route("/update", methods=["POST"])
@validate("user_update_req")
def updateUser():
    if "role" in g.payload and g.payload["role"] not in [SystemRole.USER.value]:
        raise APIException(message="This user role cannot be registered using this path at the moment", status_code=403)
    
    u = controller.get_user_by_id(g.session["userID"])
    
    # Check for trial period
    check_trial(u)
    
    controller.update_user(u, **g.payload)

    return response(success=True)

@user.route("/trial", methods=["PUT"])
@validate("user_trial_add_req")
def setUserTrialPeriod():
    user_id = g.session["userID"]
    session_user = controller.get_user_by_id(user_id)
    if session_user.role not in [SystemRole.GLOBAL_ADMIN.value]:
        raise APIException(message="Only global admin has access to this endpoint", status_code=403)
    
    target_user_id = g.payload["user_id"]
    target_user = controller.get_user_by_id(target_user_id)
    in_the_past = g.payload["in_the_past"]
    
    if in_the_past:
        end_date = datetime.datetime.now() - datetime.timedelta(days=TRIAL_PERIOD)
    else:
        end_date = datetime.datetime.now() + datetime.timedelta(days=TRIAL_PERIOD)
        
    controller.update_user(target_user, trial_period_expire_date=end_date)

    return response(success=True)

@user.route("/trial", methods=["DELETE"])
@validate("user_trial_remove_req")
def removeUserTrialPeriod():
    user_id = g.session["userID"]
    session_user = controller.get_user_by_id(user_id)
    if session_user.role not in [SystemRole.GLOBAL_ADMIN.value]:
        raise APIException(message="Only global admin has access to this endpoint", status_code=403)
    
    target_user_id = g.payload["user_id"]
    target_user = controller.get_user_by_id(target_user_id)
    
    controller.update_user(target_user, trial_period_expire_date="delete")

    return response(success=True)

@user.route("/login", methods=["POST"])
@noauth
@validate("user_login_req")
def loginUser():
    u = controller.get_user_by_mail(g.payload["mail"])
    if not u or not u.password_hash:
        raise InvalidCredentialsError()

    password_hash = hash_password(g.payload["password"] + u.password_salt)
    if password_hash == u.password_hash:
        token = auth.start_session(user_id=u.id,user_role=u.role)
        return response(payload={"token" : token})
    else:
        raise InvalidCredentialsError()

@user.route("/logout", methods=["POST"])
def logoutUser():
    auth.destroy_session(g.session["sessionToken"])
    return response(success=True)

def _check_password(password):
    return (len(password) > 4)

class InvalidPasswordFormatError(APIException):
    def __init__(self):
        super(InvalidPasswordFormatError, self).__init__(status_code=400, error_code=1201, message="Password must be at least 5 characters in length")

class UsernameTakenError(APIException):
    def __init__(self):
        super(UsernameTakenError, self).__init__(status_code=409, error_code=1202, message="The e-mail is already registered in the system")

class InvalidCredentialsError(APIException):
    def __init__(self):
        super(InvalidCredentialsError, self).__init__(status_code=403, error_code=1203, message="Username and password do not match a user account")

class SessionAlreadyRegisteredError(APIException):
    def __init__(self):
        super(SessionAlreadyRegisteredError, self).__init__(status_code=422, error_code=1204, message="The session is already registered to another user")

class InvitationExpiredError(APIException):
    def __init__(self):
        super(InvitationExpiredError, self).__init__(status_code=423, error_code=1205, message="The invitation is no longer valid")

class TrialPeriodExpiredError(APIException):
    def __init__(self):
        super(TrialPeriodExpiredError, self).__init__(status_code=423, error_code=1206, message="The trial period has expired")