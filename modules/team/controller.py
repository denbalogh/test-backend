"""
Data controller for team ressources
"""

from datetime import datetime
from operator import add
from typing import Union

from flask import g
import sqlalchemy

from database import db
from modules.user import controller as user_controller
from modules.team.error import CoachMemberConflictError
from model.User import User
from model.Roles import SystemRole, OrgRole, TeamRole
from model.Team import Team, TeamMember
from error import NotFoundError
from util.auth import AccessDeniedError, require, refresh_user_access, revoke_user_access

def get_team_by_id(team_id):
    """Returns a team object by team ID, raises a NotFoundError if no team was found"""
    if team_id == "current" and g.session["userRole"] == "member":
        team_id = g.session["team"]
    
    try:
        team = Team.query.filter_by(id=team_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        raise NotFoundError()

    if not require(TeamRole.ANY, team_id, raise_exception=False):
        require(OrgRole.COMPANY_ADMIN, team.company.id)

    return team

def get_teams():
    return Team.query.filter_by().all()

def get_user_teams(restrict_to_role: Union[TeamRole, bool] = True):
    """Get a list of all teams the user can see"""
    if g.session["userRole"] == SystemRole.GLOBAL_ADMIN:
        return Team.query.all()
    else:
        if "team" in g.session:
            user_teams = [get_team_by_id(g.session["team"])]
        elif type(restrict_to_role) is bool and restrict_to_role:
            user_teams = Team.query.filter(
                Team.team_members.any(
                    sqlalchemy.and_(
                        TeamMember.user_id == g.session["userID"],
                        TeamMember.role != TeamRole.MEMBER
                    )
                )
            ).all()
        elif restrict_to_role is not None:
            user_teams = Team.query.filter(
                Team.team_members.any(
                    sqlalchemy.and_(
                        TeamMember.user_id == g.session["userID"],
                        TeamMember.role == restrict_to_role)
                    )
                ).all()
        else:
            user_teams = Team.query.filter(Team.members.any(User.id == g.session["userID"])).all()
        
        return user_teams

def create_team(name, members=None):
    team = Team(name=name)
    db.session.add(team)
    db.session.commit()
    
    coach = user_controller.get_user_by_id(g.session["userID"])

    if not members:
        members = []
    else:
        members = [m for m in members if m["mail"] != coach.mail]

    members.append({"mail": coach.mail, "role": TeamRole.MANAGER})

    if members:
        add_team_members(team, members, skip_access_check=True)

    return team

def update_team(team, name=None):
    ensure_team_edit_privileges(team)
    
    if name is not None:
        team.name = name

    db.session.commit()

    return team

def add_team_members(team, members, skip_access_check=False):
    if not skip_access_check:
        ensure_team_edit_privileges(team)

    member_users = {member["mail"]: user_controller.get_user_by_mail(member["mail"]) for member in members} 

    for member in members:
        user = member_users[member["mail"]]

        if "role" in member:
            role = TeamRole(member["role"])
        else:
            role = TeamRole.MEMBER

        team_member = None
        if user is None:
            user = user_controller.create_user(member["mail"])
        else:
            team_member = TeamMember.query.filter(TeamMember.user_id == user.id, TeamMember.team_id == team.id).one_or_none()
            if team_member is not None:
                # If user is already part of the team, update the role
                team_member.role = TeamRole(member["role"])
                refresh_user_access(user, role, team.id)

        if team_member is None:
            # If not already part of the team
            team_member = TeamMember()
            team_member.team = team
            team_member.user = user
            team_member.role = role
            db.session.add(team_member)
            team.team_members.append(team_member)
            refresh_user_access(user, role, team.id)

    db.session.commit()

    return team

def remove_team_members(team, members):
    """Removes a user from a team, raises a NotFoundError if no association entry was found"""
    ensure_team_edit_privileges(team)
    
    for m in members:
        try:
            user = user_controller.get_user_by_mail(m)

            tm = TeamMember.query.filter(TeamMember.user == user, TeamMember.team == team).one_or_none()
            if tm:
                revoke_user_access(user.id, team_id=team.id)
                team.team_members.remove(tm)

        except ValueError:
            raise NotFoundError()

    db.session.commit()

    return team

def ensure_team_edit_privileges(team):
    """Returns True if current user is coach of the given team, raises a AccessDeniedError if not"""
    if not require(TeamRole.MANAGER, team.id, raise_exception=False):
        require(OrgRole.COMPANY_ADMIN, team.company.id)
    return True
