from django.contrib.auth import get_user_model
from rest_framework import generics, mixins, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    RegisterSerializer, LoginSerializer, LogoutSerializer, ProfileSerializer,
    ProjectSerializer, TaskSerializer, DocumentSerializer, CommentSerializer,
    NotificationSerializer, TimeLineSerializer
)
from .models import Project, Task, Document, Comments, Notification, TimeLine, Profile

User = get_user_model()


# ----------------- Auth APIs -----------------
class RegisterView(mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "email": user.email,
            "username": user.username,
        }, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)


# ----------------- Profile -----------------
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        try:
            return self.request.user.profile
        except Profile.DoesNotExist:
            return Profile.objects.create(
                user=self.request.user,
                phone="", 
                role="manager"  
            )

# ----------------- Project -----------------
class ProjectListCreateView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        self.queryset = Project.objects.filter(team_members=request.user)
        return Response({"status": "success", "data": self.list(request, *args, **kwargs).data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        try:
           
            profile = request.user.profile
        except Profile.DoesNotExist:
           
            return Response({
                "status": "error",
                "message": "Profile not found. Please complete your profile first."
            }, status=status.HTTP_403_FORBIDDEN)
        
        if profile.role != "manager":  
            return Response({
                "status": "error",
                "message": "Only Manager can create projects"
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = serializer.save(owner=request.user)
        project.team_members.add(request.user)
        return Response({
            "status": "success", 
            "message": "Project created", 
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    
class AddMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            project = Project.objects.get(pk=pk, owner=request.user)
        except Project.DoesNotExist:
            return Response({"status": "error", "message": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"status": "error", "message": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"status": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        project.team_members.add(user)
        return Response({"status": "success", "message": f"{user.username} added to project", "data": {"project": project.title, "member": user.username}}, status=status.HTTP_200_OK)


class ProjectDetailView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(team_members=self.request.user)


# ----------------- Task -----------------
class TaskListCreateView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(project__team_members=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        profile = request.user.profile
        if profile.role != "Manager":
            return Response({"status":"error","message":"Only Manager can create tasks"}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TaskDetailView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile = self.request.user.profile
        if profile.role == "Manager":
            return Task.objects.filter(project__team_members=self.request.user)
        else:
            return Task.objects.filter(assignee=self.request.user)


class AssignTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        profile = request.user.profile
        if profile.role != "Manager":
            return Response({"status":"error","message":"Only Manager can assign tasks"}, status=status.HTTP_403_FORBIDDEN)
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        user_id = request.data.get("assignee_id")
        if not user_id:
            return Response({"error": "Assignee ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(pk=user_id)
            if user not in task.project.team_members.all():
                return Response({"error": "User is not a member of this project"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        task.assignee = user
        task.save()
        return Response({"message": f"Task '{task.title}' assigned to {user.username or user.email}"}, status=status.HTTP_200_OK)


# ----------------- Document -----------------
class DocumentView(mixins.CreateModelMixin, mixins.ListModelMixin, generics.GenericAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Document.objects.filter(project__team_members=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(uploaded_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DocumentDetailView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(project__team_members=self.request.user)


# ----------------- Comment -----------------
class CommentListCreateView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Comments.objects.filter(project__team_members=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentDetailView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Comments.objects.filter(author=self.request.user)


# ----------------- Notifications -----------------
class NotificationView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


class MarkNotificationReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def patch(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.mark_read = True
        notification.save()
        return Response({"message": "Notification marked as read", "data": NotificationSerializer(notification).data})


# ----------------- Timeline -----------------
class TimeLineListView(generics.ListAPIView):
    serializer_class = TimeLineSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs.get("project_id")
        return TimeLine.objects.filter(project_id=project_id).order_by("-time")
