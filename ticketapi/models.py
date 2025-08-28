from django.db import models

from api.models import CustomUser
# Create your models here.

class RoleChoice(models.TextChoices):
    MANAGER='manager','Manager'
    DEVELOPER='developer','Developer'
    QA='qa','Qa'
    DESIGNER='designer','Designer'


class Profile(models.Model):
    user=models.OneToOneField(CustomUser,on_delete=models.CASCADE,related_name='profile')
    profile_picture=models.ImageField(upload_to='profile_pics/',blank=True,null=True)
    phone=models.CharField(max_length=20)
    role=models.CharField(
        max_length=20,
        choices=RoleChoice.choices,
        default=RoleChoice.MANAGER
    )

    def __str__(self):
        return f"{self.user} - {self.role}"
    

class Project(models.Model):
    title=models.CharField(max_length=25)
    description=models.TextField()
    start_date=models.DateField()
    end_date=models.DateField(blank=True,null=True)
    team_members=models.ManyToManyField(CustomUser,related_name='projects')


class TaskStatus(models.TextChoices):
    OPEN = 'open', 'Open'
    WORKING = 'working', 'Working'
    REVIEW = 'review', 'Review'
    WAITING_QA = 'waiting_qa', 'Waiting QA'
    AWAITING_RELEASE = 'awaiting_release', 'Awaiting Release'
    CLOSED = 'closed', 'Closed'


class Task(models.Model):
    title=models.CharField(max_length=30)
    description=models.TextField()
    status=models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.OPEN
    )
    project=models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    assignee=models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="tasks"    
    )

    def __str__(self):
        return self.title
    

class  Document(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=30)
    file = models.FileField(upload_to='documents/')
    version = models.CharField(max_length=15, default='1.0')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    

class Comments(models.Model):
    text = models.TextField(max_length=300)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.task}"
    
    
class TimeLine(models.Model):
    EVENT_CHOICES = [
        ("created", "Created"),
        ("updated", "Updated"),
        ("deleted", "Deleted"),
    ]
    event_type=models.CharField(max_length=20,choices=EVENT_CHOICES)
    time=models.DateTimeField(auto_now_add=True)
    project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name="timeline")
    def __str__(self):
        return f"{self.project.title} - {self.event_type} at {self.time}"
    

class Notification(models.Model):
    text=models.TextField()
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="notification")
    created_at=models.DateTimeField(auto_now_add=True)
    mark_read=models.BooleanField(default=False)  
    def __str__(self):
        return f"Notification for {self.user.email} - {self.text[:20]}"