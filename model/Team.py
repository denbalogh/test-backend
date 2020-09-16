"""
Team model definition
"""

from sqlalchemy.ext.associationproxy import association_proxy

from database import db
from model.User import User
from model.Roles import TeamRole

class TeamMember(db.Model):
    __tablename__ = "team_members"

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"), primary_key=True)

    user = db.relationship("User", back_populates="team_memberships")
    team = db.relationship("Team", back_populates="team_members")

    role = db.Column(db.Enum(TeamRole), default=TeamRole.MEMBER)

class Team(db.Model):
    """Represents a team"""
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String)

    team_members = db.relationship(TeamMember, back_populates="team", cascade="all, delete-orphan")
    members = association_proxy("team_members", "user")

    def to_response(self):
        return {
            "id": self.id,
            "name": self.name
        }

    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name})>"
