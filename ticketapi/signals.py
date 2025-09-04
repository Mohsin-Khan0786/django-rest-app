from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Comments, Notification, Project, Task, TimeLine

User = get_user_model()


@receiver(post_save, sender=Project)
def create_project_timeline(sender, instance, created, **kwargs):
    """Create timeline event when project is created/updated"""
    if created:
        TimeLine.objects.create(project=instance, event_type="created")
    else:
        TimeLine.objects.create(project=instance, event_type="updated")


@receiver(post_delete, sender=Project)
def create_project_deleted_timeline(sender, instance, **kwargs):
    """Create timeline event when project is deleted"""
    TimeLine.objects.create(project=instance, event_type="deleted")


@receiver(post_save, sender=Task)
def create_task_timeline_and_notifications(sender, instance, created, **kwargs):
    if created:
        TimeLine.objects.create(project=instance.project, event_type="created")
    else:
        TimeLine.objects.create(project=instance.project, event_type="updated")

    if instance.assignee:
        Notification.objects.create(
            user=instance.assignee,
            text=f"You have been assigned to task: {instance.title}",
        )


@receiver(post_delete, sender=Task)
def create_task_deleted_timeline(sender, instance, **kwargs):
    """Create timeline event when task is deleted"""
    TimeLine.objects.create(project=instance.project, event_type="deleted")


@receiver(post_save, sender=Comments)
def create_comment_notifications(sender, instance, created, **kwargs):
    """Create notifications when comments are added to tasks"""
    if created and instance.task and instance.task.assignee:

        if instance.author != instance.task.assignee:
            Notification.objects.create(
                user=instance.task.assignee,
                text=f"New comment on task '{instance.task.title}' by {instance.author.email}",
            )
