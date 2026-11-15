from django.shortcuts import render
from .serializers import RegisterSerializer, UserSerializer
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from rest_framework.viewsets import ViewSet, ModelViewSet,ReadOnlyModelViewSet
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from complaints.permissions import IsAdminOrReadOnly, IsAdminOfficerOrReadOnly
from rest_framework.response import Response
from complaints.models import Department
from rest_framework.exceptions import ValidationError, PermissionDenied


# Create your views here.
class RegisterAPIView(generics.CreateAPIView):
	queryset = User.objects.all()
	serializer_class = RegisterSerializer
	permission_classes = [AllowAny]


class MeAPIView(generics.RetrieveAPIView):

	serializer_class= UserSerializer

	def get_object(self):
		return self.request.user

class UserManagementViewSet(ReadOnlyModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	permission_classes = [IsAuthenticated, IsAdminOfficerOrReadOnly]

	@action(
		detail=True,
		methods=['post'],
		url_path="assign_department",
		permission_classes=[IsAuthenticated, IsAdminOrReadOnly]
		)
	def assign_department(self, request, *args, **kwargs):

		selected_department_id = request.data.get('department_id')

		if not selected_department_id:
			raise ValidationError("Department Id is required.")

		officer = get_object_or_404(User, id=kwargs["pk"])
		department = get_object_or_404(Department, id=selected_department_id)

		if officer.role != "officer":
			raise PermissionDenied("Departments can only be assigned to officers.")

		officer.department= department
		officer.save()

		return Response({
		"msg": "Department assigned to the selected officer.",
		"status": True,
		"body" : UserSerializer(officer).data
		})
