"""
User role definitions
"""

from enum import Enum, EnumMeta

class EnumAnyType:
    value = "any"
    order = -1

    def __init__(self, type):
        self._type = type
        return super(EnumAnyType, self).__init__()

    @property
    def __class__(self):
        return self._type

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return True
        if type(other) == ComparableOrderedStringEnum or type(other) == str:
            return False
        return NotImplemented
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return False
        if type(other) == ComparableOrderedStringEnum or type(other) == str:
            return False
        return NotImplemented
    def __le__(self, other):
        if self.__class__ is other.__class__:
            return True
        if type(other) == ComparableOrderedStringEnum or type(other) == str:
            return True
        return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return False
        if type(other) == ComparableOrderedStringEnum or type(other) == str:
            return True
        return NotImplemented

    def __eq__(self, other):
        return type(other) == type(self)

class EnumAnyMeta(EnumMeta):
    def __getattr__(cls, name: str):
        if name.lower() == "any":
            # print(cls.__name__)
            return EnumAnyType(cls)
        else:
            return super(EnumAnyMeta, cls).__getattr__(name)

class ComparableOrderedStringEnum(Enum, metaclass=EnumAnyMeta):
    order: int

    def __new__(cls, name: str, order: int):
        obj = object.__new__(cls)
        obj._value_ = name
        obj.order = order
        return obj

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.order >= other.order
        elif type(other) == str:
            return self.order >= type(self)(other).order
        elif type(other) == EnumAnyType:
            return True
        return NotImplemented
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.order > other.order
        elif type(other) == str:
            return self.order > type(self)(other).order
        elif type(other) == EnumAnyType:
            return True
        return NotImplemented
    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.order <= other.order
        elif type(other) == str:
            return self.order <= type(self)(other).order
        elif type(other) == EnumAnyType:
            return False
        return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.order < other.order
        elif type(other) == str:
            return self.order <= type(self)(other).order
        elif type(other) == EnumAnyType:
            return False
        return NotImplemented

    def __eq__(self, other):
        if type(other) == type(self): 
            return self.value == other.value
        elif type(other) == str:
            return self.value == other
        else:
            return False

    def __hash__(self):
        return hash(self.value)

class SystemRole(ComparableOrderedStringEnum):
    """
    System wide roles with the scope of a session
    """
    GLOBAL_ADMIN = "admin", 3
    USER = "coach", 2
    PARTICIPANT = "member", 1

class OrgRole(ComparableOrderedStringEnum):
    """
    User roles on organization level
    """
    COMPANY_ADMIN = "company_admin", 3
    OPERATOR = "company_operator", 2
    USER = "company_user", 1

class TeamRole(ComparableOrderedStringEnum):
    """
    User roles on team level
    """
    MANAGER = "team_manager", 4
    COACH = "team_coach", 3
    MEMBER = "team_member", 2
    READER = "team_reader", 1
