from enum import Enum


class RoleChoice(Enum):
    MANAGER = "manager"
    DEVELOPER = "developer"
    QA = "qa"
    DESIGNER = "designer"


class TaskStatus(Enum):
    OPEN = "open"
    WORKING = "working"
    REVIEW = "review"
    WAITING_QA = "waiting_qa"
    AWAITING_RELEASE = "awaiting_release"
    CLOSED = "closed"


class EventType(Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
