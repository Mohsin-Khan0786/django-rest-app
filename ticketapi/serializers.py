from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import Project, Task, Document, Comments, Notification


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "email", "password", "username"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


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

    def save(self, **kwargs):
        try:
            RefreshToken(self.validated_data['refresh']).blacklist()
        except TokenError:
            self.fail("bad_token")


class ProjectSerializer(serializers.ModelSerializer):
    team_members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )
    created_by = serializers.ReadOnlyField(source='created_by.id')

    class Meta:
        model = Project
        fields = ["id", "title", "description", "start_date", "end_date", "team_members", "created_by"]


class TaskSerializer(serializers.ModelSerializer):
    assignee_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = ["id", "title", "description", "status", "project", "assignee", "assignee_details"]

    def get_assignee_details(self, obj):
        if obj.assignee:
            return {"id": obj.assignee.id, "username": obj.assignee.username}
        return None


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.ReadOnlyField(source='uploaded_by.username')

    class Meta:
        model = Document
        fields = ["id", "name", "description", "file", "version", "project", "uploaded_by"]


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comments
        fields = ['id', 'text', 'author', 'author_name', 'task', 'project', 'created_at']
        read_only_fields = ["author", "created_at"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'text', 'user', 'created_at', 'mark_read']
        read_only_fields = ['user', 'created_at']