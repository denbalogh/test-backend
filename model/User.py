"""
User model definition
"""

from sqlalchemy.ext.associationproxy import association_proxy

from database import db
from .Roles import OrgRole, SystemRole, TeamRole

class User(db.Model): # type: ignore
    """Represents a user"""
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String)
    
    mail = db.Column(db.String, unique=True)

    registered = db.Column(db.Boolean)

    password_hash = db.Column(db.String)
    password_salt = db.Column(db.String)

    role = db.Column(db.Enum(SystemRole), default=SystemRole.PARTICIPANT)

    team_memberships = db.relationship("TeamMember", back_populates="user", cascade="all,delete-orphan")
    teams = association_proxy("team_members", "team")

    def __repr__(self):
        return "<User(id=%s, mail=%s, role=%s)>" % (
            self.id, self.mail, self.role
        )
