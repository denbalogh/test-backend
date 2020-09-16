"""User routes

Blueprint defining routes for user and session management.
"""

from flask import Blueprint, g, request, make_response

from model.Roles import OrgRole, TeamRole
from modules.team import controller
from modules.user import controller as user_controller
from model.Roles import SystemRole
from error import APIException, NotFoundError, BadParameterError
from util import response, validate
from util.auth import restrict_to, require
from util.structs import UserInputDict

team = Blueprint("team", __name__)

@team.route("", methods=["GET"])
def listTeams():
    payload = []

    user_teams = controller.get_user_teams()

    payload = [t.to_response() for t in user_teams]

    return response(payload={"teams" : payload})

@team.route("", methods=["POST"])
@restrict_to(SystemRole.USER)
@validate("team_create_req")
def createTeam():
    data = g.payload
    members = None
    questions = None
    if "members" in data:
        members = data["members"]
    if "questions" in data:
        questions = data["questions"]

    team = controller.create_team(data['name'], members, questions)

    return(response(payload={"id": str(team.id)}))

@team.route("/<teamId>", methods=["GET"])
def getTeam(teamId):
    team = controller.get_team_by_id(teamId)

    members = []
    for m in team.members:
        members.append({"id": m.id, "mail": m.mail, "role": str(m.role)})
    
    payload = {
        "name" : team.name,
        "members" : members
    }
    
    return response(payload=payload)

@team.route("/<teamId>", methods=["PATCH"])
@restrict_to(SystemRole.USER)
@validate("team_update_req")
def updateTeam(teamId):
    team = controller.get_team_by_id(teamId)
    controller.update_team(team, g.payload["name"])

    return response(success=True)

@team.route("/<teamId>/members", methods=["GET"])
def listTeamMembers(teamId):
    team = controller.get_team_by_id(teamId)

    members = []
    for m in team.members:
        current_member = {
            "id" : str(m.id),
            "mail": m.mail
        }
        if m.name is not None:
            current_member["name"] = m.name
        if m.role is not None:
            current_member["role"] = m.role.value
        members.append(current_member)

    return response(payload={"members": members})

@team.route("/<teamId>/members", methods=["PATCH"])
@restrict_to(SystemRole.USER)
@validate("team_member_add_req")
def addTeamMembers(teamId):
    team = controller.get_team_by_id(teamId)
    controller.add_team_members(team, g.payload["members"])

    return response(success=True)

@team.route("/<teamId>/members", methods=["DELETE"])
@restrict_to(SystemRole.USER)
def removeTeamMember(teamId):
    members = request.args.get('members').split(",")
    team = controller.get_team_by_id(teamId)

    controller.remove_team_members(team, members)
    
    return response(success=True)
