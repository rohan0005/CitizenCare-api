from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model= User
		fields = ["id", "username", "email", "first_name", "last_name", "role", "phone_number", "department"]

	read_only_fields = ["id", "role"]


class RegisterSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True, min_length=6, validators=[validate_password])

	class Meta:
		model = User
		fields = ["id", "username", "password" ,"email", "first_name", "last_name", "phone_number", ]

	def validate_phone_number(self, value):
		if value and (not value.isdigit() or len(value) < 10):
			raise serializers.ValidationError(
				"Enter a valid phone number (at least 10 digits).")
		return value

	def create(self,validated_data):
		password = validated_data.pop("password")

		validated_data["role"] = User.Role.CITIZEN
		validated_data["department"] = None

		user = User.objects.create_user(password=password,**validated_data)

		return user
