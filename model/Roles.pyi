from enum import Enum
from typing import Union

class EnumAnyType: ...

class ComparableOrderedStringEnum(Enum):
    order: int

    def __init__(self, value: str) -> ComparableOrderedStringEnum: ...

    def __ge__(self, other: Union[ComparableOrderedStringEnum, str]) -> bool: ...
    def __gt__(self, other: Union[ComparableOrderedStringEnum, str]) -> bool: ...
    def __le__(self, other: Union[ComparableOrderedStringEnum, str]) -> bool: ...
    def __lt__(self, other: Union[ComparableOrderedStringEnum, str]) -> bool: ...
    def __eq__(self, other: Union[ComparableOrderedStringEnum, str]) -> bool: ...

class SystemRole(ComparableOrderedStringEnum):
    GLOBAL_ADMIN: SystemRole
    USER: SystemRole
    PARTICIPANT: SystemRole
    ANY: EnumAnyType

class OrgRole(ComparableOrderedStringEnum):
    COMPANY_ADMIN: OrgRole
    OPERATOR: OrgRole
    USER: OrgRole
    ANY: EnumAnyType

class TeamRole(ComparableOrderedStringEnum):
    MANAGER: TeamRole
    COACH: TeamRole
    MEMBER: TeamRole
    READER: TeamRole
    ANY: EnumAnyType

