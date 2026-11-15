from rest_framework.viewsets import ModelViewSet
from .serializers import ComplaintSerializer, DepartmentSerializer, CategorySerializer
from .models import Complaint, Category, Department
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from accounts.models import User

class DepartmentViewSet(ModelViewSet):
	serializer_class= DepartmentSerializer
	permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

	queryset = Department.objects.all()

class CategoryViewSet(ModelViewSet):
	serializer_class= CategorySerializer
	permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

	queryset = Category.objects.all()


#business logic: admin cannot assign a complaint to an officer from the wrong department
class ComplaintViewSet(ModelViewSet):
	serializer_class = ComplaintSerializer
	permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
	lookup_field = "tracking_id"

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


	def update(self, request, *args, **kwargs):
		complaint = self.get_object()

		if request.user.role == "citizen":
			if complaint.status != Complaint.Status.SUBMITTED:
				raise PermissionDenied(f"You can only edit complaints while they are submitted. Current Status is: {complaint.status}")

			allowed_fields = ('title', 'description')
			submitted_fields = set(request.data.keys())

			if not submitted_fields.issubset(allowed_fields):
				raise PermissionDenied("You can only update the title and description.")

		return super().update(request, *args, **kwargs)

	@action(
		detail=True,
		methods=["post"],
		permission_classes=[IsAuthenticated,IsAdminOrReadOnly]
		)
	def assign(self, request, *args, **kwargs):
		complaint = self.get_object()

		selected_user_id = request.data.get('officer_id')

		if not selected_user_id:
			raise ValidationError("Officer Id is required.")

		officer = get_object_or_404(User, id=selected_user_id)

		if officer.role != "officer":
			raise PermissionDenied("You can only assign complaints to an officer.")

		if officer.department != complaint.category.department:
			raise PermissionDenied({
				"status": False,
				"msg": "Department mismatch. You can only assign complaints to the same department.",
				"detail": {
				"officer_department": str(officer.department),
            	"complaint_department": str(complaint.category.department)
				}
				})

		complaint.assigned_to = officer
		complaint.status = Complaint.Status.ASSIGNED
		complaint.save()

		return Response({
			"msg": "Complaint assigned to officer.",
			"status": True,
			"body": self.get_serializer(complaint).data
			})

	@action(
		detail=True,
		methods=['post'],
		url_path="change-status",
		permission_classes=[IsAuthenticated]
		)
	def update_status(self, request, *args, **kwargs):
		allowed_transitions = {
		"assigned": ["in_progress", "rejected"],
		"in_progress": ["resolved", "rejected"],
		"resolved": ["closed", "in_progress"],
		"closed": [],
		"rejected": []
		}

		complaint = self.get_object()

		updated_status = request.data.get('status')

		updated_status = updated_status.lower()
		current_status = complaint.status

		if request.user.role != "officer":
			raise PermissionDenied("Only assigned officers can update complaint status.")

		if complaint.assigned_to != request.user:
			raise PermissionDenied("You can only change the status of complaints assigned to you.")

		if not isinstance(updated_status, str):
			raise ValidationError("Status must be a string.")

		if updated_status not in allowed_transitions.get(current_status, []):
			raise ValidationError(
				f"Cannot change status from {current_status} to {updated_status}.")

		complaint.status = updated_status
		complaint.save()

		return Response({"msg": "Complaint Status Updated.",
			"status": True,
			"body": self.get_serializer(complaint).data
			})




