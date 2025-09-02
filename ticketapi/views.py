from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import IsManager,IsCommentAuthor
from .models import (
    Profile, 
    Project, Task, Document,
    Comments, Notification, TimeLine
)
from .serializers import (
    RegisterSerializer, LoginSerializer, LogoutSerializer,
    ProjectSerializer, TaskSerializer, DocumentSerializer,
    CommentsSerializer, TimeLineSerializer, NotificationSerializer,
    AssignTaskSerializer, MarkNotificationReadSerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get("user")
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "email": user.email,
            "username": user.username,
        }, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"msg": "Logout successful"},
            status=status.HTTP_205_RESET_CONTENT
        )


class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Project.objects.filter(
            team_members=self.request.user
        ).prefetch_related('team_members')
    
    def perform_create(self, serializer):
        project = serializer.save()
        project.team_members.add(self.request.user)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self):
        return Project.objects.filter(
            team_members=self.request.user
        ).prefetch_related('team_members', 'tasks')


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self):
        user = self.request.user
        project_id = self.request.query_params.get('project_id')

        queryset = Task.objects.filter(
            project__team_members=user
        ).select_related(
            'project', 'assignee'
        ).prefetch_related(
            'project__team_members', 'comments'
        )

        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self):
        return Task.objects.filter(
            project__team_members=self.request.user
        ).select_related('project', 'assignee')


class AssignTaskView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]
    serializer_class = AssignTaskSerializer

    def post(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            assignee_id = serializer.validated_data['assignee_id']
            assignee = get_object_or_404(User, id=assignee_id)
            task.assignee = assignee
            task.save()
            
            return Response({
                "message": f"Task '{task.title}' assigned to {assignee.email}",
                "task": TaskSerializer(task).data
            }, status=status.HTTP_200_OK)
        

class DocumentView(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        project_id = self.request.query_params.get('project_id')
        
        queryset = Document.objects.filter(
            project__team_members=user
        ).select_related('project')
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
    

class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(
            project__team_members=self.request.user
        ).select_related('project') 


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        task_id = self.request.query_params.get('task_id')
        project_id = self.request.query_params.get('project_id')
        
        queryset = Comments.objects.filter(
            task__project__team_members=user
        ).select_related(
            'author', 'task', 'project'
        )
        
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentsSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentAuthor]

    def get_queryset(self):
        return Comments.objects.filter(task__project__team_members=self.request.user)


class TimeLineListView(generics.ListAPIView):
    serializer_class = TimeLineSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        project_id = self.request.query_params.get('project_id')
        
        queryset = TimeLine.objects.filter(
            project__team_members=user
        ).select_related('project')

        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset.order_by('-time')


class NotificationView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).select_related('user').order_by('-created_at')


class MarkNotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, pk):
        notification = get_object_or_404(Notification, id=pk, user=request.user)
        serializer = MarkNotificationReadSerializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            notification.mark_read = serializer.validated_data['mark_read']
            notification.save()
            
            return Response({
                "message": "Notification updated successfully",
                "notification": NotificationSerializer(notification).data
            }, status=status.HTTP_200_OK)
