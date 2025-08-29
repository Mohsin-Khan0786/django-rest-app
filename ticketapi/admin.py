from django.contrib import admin
from .models import Profile, Project, Task, Document, Comments, Notification, TimeLine

admin.site.register(Project)
admin.site.register(Profile)
admin.site.register(Task)
admin.site.register(Document)
admin.site.register(Comments)
admin.site.register(Notification)
admin.site.register(TimeLine)
