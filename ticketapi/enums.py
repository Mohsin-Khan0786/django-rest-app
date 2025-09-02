from django.db import models


class RoleChoice(models.TextChoices):
    MANAGER = 'manager', 'Manager'
    DEVELOPER = 'developer', 'Developer'
    QA = 'qa', 'Qa'
    DESIGNER = 'designer', 'Designer'


class TaskStatus(models.TextChoices):
    OPEN = 'open', 'Open'
    WORKING = 'working', 'Working'
    REVIEW = 'review', 'Review'
    WAITING_QA = 'waiting_qa', 'Waiting QA'
    AWAITING_RELEASE = 'awaiting_release', 'Awaiting Release'
    CLOSED = 'closed', 'Closed'


class EventType(models.TextChoices):
    CREATED = 'created', 'Created'
    UPDATED = 'updated', 'Updated'
    DELETED = 'deleted', 'Deleted'
