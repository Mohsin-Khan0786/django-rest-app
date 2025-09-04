from django.contrib import admin

from .models import Comments, Document, Notification, Profile, Project, Task, TimeLine

admin.site.register(Project)
admin.site.register(Profile)
admin.site.register(Task)
admin.site.register(Document)
admin.site.register(Comments)
admin.site.register(Notification)
admin.site.register(TimeLine)
