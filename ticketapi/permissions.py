from rest_framework.permissions import BasePermission
from django.shortcuts import get_object_or_404
from .models import Profile

class IsManager(BasePermission):
    """
    Allow access only to Managers.
    """
    def has_permission(self, request, view):
        profile = get_object_or_404(Profile, user=request.user)
        return profile.role == "manager"

class IsCommentAuthor(BasePermission):
    """
    Allow comment update/delete only by author.
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
