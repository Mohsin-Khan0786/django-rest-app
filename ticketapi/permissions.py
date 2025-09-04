from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from .enums import RoleChoice
from .models import Profile


class IsManager(BasePermission):
    """
    Only managers can create/update/delete projects.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        profile = get_object_or_404(Profile, user=request.user)
        return profile.role == RoleChoice.MANAGER.name


# class IsManagerOrReadOnlyForTasks(BasePermission):
#     """
#     - Managers: can create/update/delete tasks
#     - Other team members: can only view tasks assigned to their project
#     """

#     def has_permission(self, request, view):
#         if not request.user or not request.user.is_authenticated:
#             return False

#         if request.method in ("GET", "HEAD", "OPTIONS"):
#             return True
#         profile = get_object_or_404(Profile, user=request.user)
#         return profile.role == RoleChoice.MANAGER.name

#     def has_object_permission(self, request, view, obj):
#         if request.method in ("GET", "HEAD", "OPTIONS"):
#             return request.user in obj.project.team_members.all()

#         profile = get_object_or_404(Profile, user=request.user)
#         return profile.role == RoleChoice.MANAGER.name


class IsCommentAuthor(BasePermission):
    """
    Allow comment update/delete only by the comment author.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        return obj.author == request.user
