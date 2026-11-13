from rest_framework.viewsets import ModelViewSet
from .serializers import ComplaintSerializer, DepartmentSerializer, CategorySerializer
from .models import Complaint, Category, Department
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly

class DepartmentViewSet(ModelViewSet):
	serializer_class= DepartmentSerializer
	permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

	queryset = Department.objects.all()

class CategoryViewSet(ModelViewSet):
	serializer_class= CategorySerializer
	permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

	queryset = Category.objects.all()


# Create your views here.
class ComplaintViewSet(ModelViewSet):
	serializer_class = ComplaintSerializer
	permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

	def get_queryset(self):
		user = self.request.user

		qs = Complaint.objects.select_related("category", "citizen", "assigned_to")

		if user.role == "admin":
			return qs 

		if user.role == "officer":
			return qs.filter(assigned_to = user)

		else:
			return qs.filter(citizen=user)

	def perform_create(self, serializer):
		serializer.save(citizen=self.request.user)