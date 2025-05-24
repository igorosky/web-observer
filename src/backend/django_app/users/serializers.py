from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "password", "created_at"]
        extra_kwargs = {
            'password': {'write_only': True},
            'created_at': {'read_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            password=make_password(validated_data['password'])
        )
        return user

class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password =serializers.CharField(required=True,write_only=True)

    def validate(self,data):
        email = data.get("email")
        password = data.get("password")
        if email and password:
            try:
                user = get_user_model().objects.get(email=email)
                if not user.check_password(password):
                    raise serializers.ValidationError("Password incorrect")
                data["user"] = user
                return data
            except User.DoesNotExist:
                raise serializers.ValidationError("User do not exists")
        raise serializers.ValidationError("Email and password are needed")


