from rest_framework import serializers
from api.models import CustomUser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken,TokenError

class RegisterSerializers(serializers.ModelSerializer):

    password=serializers.CharField(write_only=True)
    id=serializers.IntegerField(read_only=True)
    full_name = serializers.SerializerMethodField()
    display_name=serializers.CharField(source="username",read_only=True)


    class Meta:
        model=CustomUser 
        fields=["id","email","username","first_name","last_name","display_name","password","full_name"]


    def get_full_name(self,obj):

        return f"{obj.first_name} {obj.last_name}"
    


    def create(self,validated_data):
        password = validated_data.pop("password", None)
        user = CustomUser(**validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

class LoginSerialiazer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password")

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "email": user.email,
            "username": user.username,
        }
    

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail("bad_token")