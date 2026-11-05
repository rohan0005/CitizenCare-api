from django.shortcuts import render
from .serializers import RegisterSerializer, UserSerializer
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import User

# Create your views here.
class RegisterAPIView(generics.CreateAPIView):
	queryset = User.objects.all()
	serializer_class = RegisterSerializer
	permission_classes = [AllowAny]


class MeAPIView(generics.RetrieveAPIView):

	serializer_class= UserSerializer

	def get_object(self):
		return self.request.user