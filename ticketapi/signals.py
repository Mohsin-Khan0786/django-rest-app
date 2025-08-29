from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models.signals import post_save as django_post_save
from django.dispatch import receiver as django_receiver
from .models import Task, Comments, Document, TimeLine, Profile, CustomUser


def create_timeline_event(project, action, source):
    TimeLine.objects.create(
        project=project,
        event_type=action,
        description=f"{source} {action}" 
    )

@receiver(post_save, sender=Task)
def task_created_or_updated(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    create_timeline_event(instance.project, action, "Task")

@receiver(post_delete, sender=Task)
def task_deleted(sender, instance, **kwargs):
    create_timeline_event(instance.project, "deleted", "Task")

@receiver(post_save, sender=Comments)
def comment_created_or_updated(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    create_timeline_event(instance.project, action, "Comment")

@receiver(post_delete, sender=Comments)
def comment_deleted(sender, instance, **kwargs):
    create_timeline_event(instance.project, "deleted", "Comment")

@receiver(post_save, sender=Document)
def document_created_or_updated(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    create_timeline_event(instance.project, action, "Document")

@receiver(post_delete, sender=Document)
def document_deleted(sender, instance, **kwargs):
    create_timeline_event(instance.project, "deleted", "Document")


@django_receiver(django_post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@django_receiver(django_post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()