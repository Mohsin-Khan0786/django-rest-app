from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ProjectListCreateView, ProjectDetailView, TaskListCreateView, TaskDetailView, AssignTaskView, DocumentView, DocumentDetailView, CommentListCreateView, CommentDetailView, NotificationView, MarkNotificationReadView,ProfileView,AddMemberView,TimeLineListView

urlpatterns = [
    
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    path("profile/", ProfileView.as_view(), name="profile"),

    path('projects/', ProjectListCreateView.as_view(), name="project-list-create"),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name="project-detail"),
    path('projects/<int:pk>/add-member/', AddMemberView.as_view(), name="add-project-member"),

    path('tasks/', TaskListCreateView.as_view(), name="task-list-create"),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name="task-detail"),  
    path('tasks/<int:pk>/assign/', AssignTaskView.as_view(), name="assign-task"),
    
    path('documents/', DocumentView.as_view(), name="document-list-create"),  
    path('documents/<int:pk>/', DocumentDetailView.as_view(), name="document-detail"),  
    
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    
    path('notifications/', NotificationView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/read/', MarkNotificationReadView.as_view(), name='mark-notification-read'),

    path('projects/<int:project_id>/timeline/', TimeLineListView.as_view(), name='project-timeline'),
]