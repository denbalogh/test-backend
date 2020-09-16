"""
Data controller for user ressources
"""

import json
import random
import time

import sqlalchemy
from flask import g

from database import db
from model.User import User
from model.Roles import SystemRole, OrgRole
from error import NotFoundError
from util import hash_password, get_request_ip

from datetime import datetime, date, timedelta

def get_user_by_id(user_id):
    """Returns a user object by user ID, raises a NotFoundError if no user was found"""
    try:
        return User.query.filter_by(id=user_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        raise NotFoundError()

def get_user_by_mail(mail):
    """Searches for a user by mail, returns None if no user is found"""
    return User.query.filter_by(mail=mail).first()

def create_user(mail: str, role: SystemRole=None, password: str=None, name: str=None):
        u = User(mail=mail)
        
        if role is not None:
            u.role = role
        else:
            u.role = SystemRole.PARTICIPANT

        if name is not None:
            u.name = name

        if password is not None:
            password_salt = hash_password(str(time.time()) + str(random.random()))
            password_hash = hash_password(password + password_salt)

            u.password_hash = password_hash
            u.password_salt = password_salt

        db.session.add(u)
        db.session.commit()

        return u

def update_user(user, mail=None, role=None, password=None, name=None, hideTutorials=None, trial_period_expire_date=None):
        if mail is not None:
            user.mail = mail

        if role is not None and type(role) is SystemRole:
            user.role = role

        if name is not None:
            user.name = name
            
        if trial_period_expire_date is not None:
            user.trial_period_expire_date = trial_period_expire_date
            
        if trial_period_expire_date is 'delete':
            user.trial_period_expire_date = None

        if password is not None:
            password_salt = hash_password(str(time.time()) + str(random.random()))
            password_hash = hash_password(password + password_salt)

            user.password_hash = password_hash
            user.password_salt = password_salt

        db.session.commit()
