from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.serializers import RegisterSerializers,LoginSerialiazer,LogoutSerializer
from api.models import CustomUser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class RegisterAPIView(APIView):
    def post(self,request,format=None):
        serializer=RegisterSerializers(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        

class UserLoginView(APIView):
    def post(self, request, format=None):
        
        serializer = LoginSerialiazer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"msg": "Logout successful"},
                status=status.HTTP_205_RESET_CONTENT
            )
class DashboardView(APIView):
      permission_classes=[IsAuthenticated]

      def get(self,request):
          return Response({"msg":f"Hello {request.user.email}"})          