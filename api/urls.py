from django.urls import path
from .views import RegisterAPIView, LoginView, LogoutView, DashboardView

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),  
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
