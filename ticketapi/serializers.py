import re

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import (Profile, 
                     Project, Task,
                     Document, Comments,
                     Notification, TimeLine)

User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'profile_picture', 'phone', 'role']

    def validate_phone(self, value):
        """Phone Number must start with +92, be unique, and be 13 digits"""
        if not re.match(r'^\+92\d{10}$', value):
            raise serializers.ValidationError(
                "Phone number must start with +92 and be 13 digits long (+923001234567)."
            )

        if self.instance and Profile.objects.filter(phone=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("This phone number is already in use.")
        elif not self.instance and Profile.objects.filter(phone=value).exists():
            raise serializers.ValidationError("This phone number is already in use.")

        return value
    
    
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.SerializerMethodField()
    display_name = serializers.CharField(source="username", read_only=True)
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name", "last_name",
            "display_name", "password", "profile", "full_name"
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    def create(self, validated_data):
        profile_data = validated_data.pop("profile", None)
        password = validated_data.pop("password")
        
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        if profile_data:
            Profile.objects.create(user=user, **profile_data)
        else:
            
            Profile.objects.create(user=user)
            
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        if not check_password(password, user.password):
            raise serializers.ValidationError("Invalid email or password")

        attrs["user"] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh_token = attrs.get("refresh")
        try:
            RefreshToken(refresh_token)
        except TokenError:
            raise serializers.ValidationError("Invalid token")
        return attrs

    def save(self, **kwargs):
        RefreshToken(self.validated_data["refresh"]).blacklist()


class ProjectSerializer(serializers.ModelSerializer):
    team_members = serializers.SerializerMethodField()
    team_member_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        source='team_members',
        write_only=True,
        required=False
    )

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'start_date',
            'end_date', 'team_members', 'team_member_ids'
        ]

    def get_team_members(self, obj):
        return [
            {"id": user.id, "username": user.username, "email": user.email}
            for user in obj.team_members.all()
        ]


class TaskSerializer(serializers.ModelSerializer):
    assignee = serializers.SerializerMethodField()
    project = serializers.StringRelatedField(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False,
        allow_null=True
    )
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        source='project',
        write_only=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status',
            'project', 'project_id', 'assignee', 'assignee_id'
        ]

    def get_assignee(self, obj):
        if obj.assignee:
            return {"id": obj.assignee.id, "username": obj.assignee.username, "email": obj.assignee.email}
        return None


class DocumentSerializer(serializers.ModelSerializer):
    project = serializers.StringRelatedField(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        source='project',
        write_only=True
    )

    class Meta:
        model = Document
        fields = ['id', 'name', 'description', 'file', 'version', 'project', 'project_id']


class CommentsSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    task = serializers.StringRelatedField(read_only=True)
    project = serializers.StringRelatedField(read_only=True)
    
    task_id = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        source='task',
        write_only=True
    )
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        source='project',
        write_only=True
    )

    class Meta:
        model = Comments
        fields = ['id', 'text', 'author', 'task', 'task_id', 'project', 'project_id', 'created_at']
        read_only_fields = ['created_at']

    def get_author(self, obj):
        return {"id": obj.author.id, "username": obj.author.username, "email": obj.author.email}

    def create(self, validated_data):

        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class TimeLineSerializer(serializers.ModelSerializer):
    project = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TimeLine
        fields = ['id', 'event_type', 'time', 'project']


class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'text', 'user', 'created_at', 'mark_read']

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "email": obj.user.email
        }


class AssignTaskSerializer(serializers.Serializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )


class MarkNotificationReadSerializer(serializers.Serializer):
    mark_read = serializers.BooleanField(default=True)