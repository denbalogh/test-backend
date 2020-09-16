"""Request authentication

This module provides methods and decorators to handle authentication of
requests.
"""

from typing import Callable, Union

from flask import request, g
import time
import uuid
import hashlib
import base64
from functools import wraps
from util.RedisAdapter import RedisAdapter
from error import *

import config
from model.Roles import OrgRole, SystemRole, TeamRole, ComparableOrderedStringEnum
from model.Team import TeamMember
from model.User import User
from util import get_request_ip

_public_paths = []

def _get_request_ip():
    return get_request_ip()

def start_session(user_id, user_role):
    """Starts a new session for the given user ID"""
    token = str(uuid.uuid4())
    if config.ENVIRONMENT == "dev":
        # 12h tokens for dev environments
        expireDate = time.time() + (60 * 60 * 12)
    else:
        # New sessions will expire after 30 minutes of inactivity
        expireDate = time.time() + (60 * 30)
    session = {
        "userID" : user_id,
        "userRole" : user_role.value,
        "clientIP" : _get_request_ip(),
        "expireDate" : expireDate,
        "sessionToken" : token
    }

    # Load access roles
    teamRoles = {}
    tm_query = TeamMember.query.filter(TeamMember.user_id == user_id)
    for tm in tm_query:
        teamRoles[tm.team_id] = tm.role.value

    session["teamRoles"] = teamRoles

    g.session = session

    redis = RedisAdapter("sessions")
    redis.set(token, session)
    redis.expire(token, int(session["expireDate"]))
    return token

def destroy_session(session_id):
    """Destroys the given session"""
    redis = RedisAdapter("sessions")
    redis.unset(session_id)
    g.session = None

def _get_token():
    """Read the authentication header and syntactically validate the token"""
    if "Authorization" in request.headers:
        auth_header = request.headers["Authorization"].split(" ")
        if len(auth_header) == 2 and auth_header[0].upper() == "BEARER":
            return auth_header[1]
        else:
            raise InvalidAuthorizationHeader()
    else:
        raise NoAuthorizationHeaderError()


def authenticate(access_limit=None, set_session=True, token=False):
    """Authenticates an incoming requests and loads session information"""
    if request.endpoint in _public_paths:
        return
    elif request.method == "OPTIONS":
        return
    else:
        redis = RedisAdapter("sessions")
        if not token:
            token = _get_token()
        session = redis.get(token)
        if session is not None:
            if session["expireDate"] > time.time():
                if session["clientIP"] == _get_request_ip():
                    if access_limit is not None:
                        if type(access_limit) is not list:
                            access_limit = [access_limit]
                        if not any([r <= session["userRole"] for r in access_limit]):
                            raise AccessDeniedError()
                    # Reset expiration date for session
                    if config.ENVIRONMENT == "dev":
                        # 12h tokens for dev environments
                        session["expireDate"] = time.time() + (60 * 60 * 12)
                    else:
                        # New sessions will expire after 30 minutes of inactivity
                        session["expireDate"] = time.time() + (60 * 30)
                    if set_session:
                        g.session = session
                else:
                    raise ClientOriginViolation()
            else:
                destroy_session(token)
                raise SessionExpiredError()
        else:
            raise InvalidSessionError()

def save_session():
    """Saves the current session state"""
    if "session" in g and g.session is not None:
        token = g.session["sessionToken"]
        redis = RedisAdapter("sessions")
        redis.set(token, g.session)

def noauth(fn):
    """Decorator to disable authentication for a single path."""
    fn.is_public = True
    return fn

def restrict_to(*roles):
    """Decorator to restrict access to certain user roles"""
    def decorator(f):
        f.access_limit = [r.value for r in roles]
        @wraps(f)
        def wrapper(*args, **kw):
            return f(*args, **kw)
        return wrapper
    return decorator

def require(role: ComparableOrderedStringEnum, entity_id: int=-1, user: User=None, raise_exception: bool=True, exact: bool=False) -> bool:
    """
    Verifies if the given user has the required role on the specified entity ID.
    Type of entity is automatically deducted from type of role.

    :param role: The required role
    :param entity: The entity ID. Can be skipped (or set to -1) for system role checks
    :param user: The user object to check the role for. If not provided, the current user is used
    :param raise_exception: If set to `False`, no `AccessDeniedException` is raised when the user does not fulfill the requirement. Defaults to `True`.
    :param exact: If set to `True`, will only match if the user has the exact role. Won't work with `ANY` role
    """
    if user is not None:
        raise NotImplementedError()

    granted = False

    if SystemRole(g.session["userRole"]) == SystemRole.GLOBAL_ADMIN:
        return True

    if exact:
        comp = lambda u,c: u == c
    else:
        comp = lambda u,c: u >= c

    entity = str(entity_id)
    if isinstance(role, SystemRole):
        granted = comp(SystemRole(g.session["userRole"]), role)
    elif isinstance(role, OrgRole):
        granted = True # Not part of minimal backend example
    elif isinstance(role, TeamRole):
        granted = entity in g.session["teamRoles"] and comp(TeamRole(g.session["teamRoles"][entity]), role)

    if not granted and raise_exception:
        raise AccessDeniedError()

    return granted

def require_any(*args: Callable[[], bool], raise_exception: bool=True) -> bool:
    """
    Chain multiple requirements. Succeeds if one of the requirements is fulfilled. 
    Call as

    ```
    require_any(
        lambda: require(...),
        lambda: require(...),
        ...
    )
    ```

    :param raise_exception: If set to `False`, no `AccessDeniedException` is raised when the user does not fulfill the requirement. Defaults to `True`.
    """

    granted = False
    for f in args:
        try:
            granted = f()
        except AccessDeniedError:
            continue

    if raise_exception and not granted:
        raise AccessDeniedError()

    return granted

def require_all(*args: Callable[[], bool], raise_exception: bool=True) -> bool:
    """
    Chain multiple requirements. Succeeds if all of the requirements are fulfilled. 
    Call as

    ```
    require_any(
        lambda: require(...),
        lambda: require(...),
        ...
    )
    ```

    :param raise_exception: If set to `False`, no `AccessDeniedException` is raised when the user does not fulfill the requirements. Defaults to `True`.
    """

    granted = True
    for f in args:
        try:
            if not f():
                granted = False
                break
        except AccessDeniedError:
            granted = False
            break

    if raise_exception and not granted:
        raise AccessDeniedError()

    return granted


def refresh_user_access(user: User, role: ComparableOrderedStringEnum, entity_id: int):
    """
    Recalculate the access rights for all active sessions of the given user

    :param user: The user to update active sessions fore
    :type user: User
    :param role: The new role
    :type role: ComparableOrderedStringEnum
    :param entity_id: The affected entity
    :type entity_id: int
    """

    redis = RedisAdapter("sessions")
    sessions = redis.list()

    for key in sessions:
        try:
            if sessions[key]["userID"] == user.id:
                user_session = sessions[key]
                if isinstance(role, SystemRole):
                    user_session["userRole"] = role.value
                elif isinstance(role, OrgRole):
                    continue # Not part of minimal backend example
                elif isinstance(role, TeamRole):
                    user_session["teamRoles"][entity_id] = role.value

                redis.set(key, user_session)
        except KeyError:
            # Remove old session with invalid structure
            redis.unset(key)

    if g.session["userID"] == user.id:
        # Also update current session if affected.
        # Otherwise Redis entry will get overridden
        if isinstance(role, SystemRole):
            g.session["userRole"] = role.value
        elif isinstance(role, OrgRole):
            pass # Not part of minimal backend example
        elif isinstance(role, TeamRole):
            g.session["teamRoles"][entity_id] = role.value

def revoke_user_access(user: User, team_id: int=None):
    """
    Revoke access to an entity

    :param user: The user to revoke the access
    :type user: User
    :param team_id: Team ID, defaults to None
    :type team_id: int, optional
    :param company_id: Company ID, defaults to None
    :type company_id: int, optional
    """

    redis = RedisAdapter("sessions")
    sessions = redis.list()

    for key in sessions:
        if sessions[key]["userID"] == user.id:
            user_session = sessions[key]
            if team_id is not None and team_id in user_session["teamRoles"]:
                del user_session["teamRoles"][team_id]

            redis.set(key, user_session)

    if g.session["userID"] == user.id:
        # Also update current session if affected.
        # Otherwise Redis entry will get overridden
        if team_id is not None and team_id in g.session["teamRoles"]:
            del g.session["teamRoles"][team_id]

