from rest_framework.viewsets import ModelViewSet
from .serializers import ComplaintSerializer, DepartmentSerializer, CategorySerializer, ActivityLogSerializer, CommentSerializer, AttachmentSerializer
from .models import Complaint, Category, Department,ActivityLog, Comment,Attachment
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly, IsAuthorOrAssignedOfficer
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from accounts.models import User
from .utils import create_activity_log

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
	filterset_fields = ['status','priority', 'category']
	search_fields = ['title', 'description', 'tracking_id']
	ordering_fields =  ['created_at', 'priority', 'title']

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
		complaint = serializer.save(citizen=self.request.user)

		create_activity_log(
			complaint=complaint,
			user=self.request.user,
			action='Complaint submitted.',
			old_value='',
			new_value='Complaint submitted.',
			)


	def update(self, request, *args, **kwargs):
		complaint = self.get_object()

		if request.user.role == "citizen":
			if complaint.status != Complaint.Status.SUBMITTED:
				raise PermissionDenied(f"You can only edit complaints while they are submitted. Current Status is: {complaint.status}")

			allowed_fields = ('title', 'description')
			submitted_fields = set(request.data.keys())

			if not submitted_fields.issubset(allowed_fields):
				raise PermissionDenied("You can only update the title and description.")

		old_title = complaint.title
		old_description= complaint.description

		response = super().update(request, *args, **kwargs)

		new_title = response.data['title']
		new_description = response.data['description']


		create_activity_log(	
			complaint=complaint,
			user=self.request.user,
			action="Complaint Updated.",
			old_value=f"Title: {old_title}, Description: {old_description}",
			new_value=f"Title: {new_title}, Description: {new_description}"
			)
		return response

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

		old_officer = complaint.assigned_to
		complaint.assigned_to = officer
		complaint.status = Complaint.Status.ASSIGNED
		complaint.save()

		create_activity_log(
			complaint=complaint,
			user=request.user,
			action=f'Complaint assigned to officer.',
			old_value=str(old_officer) if old_officer else "Unassigned",
			new_value=str(officer),
			)

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

		if not isinstance(updated_status, str):
			raise ValidationError("Status must be a string.")

		updated_status = updated_status.lower()
		current_status = complaint.status

		if request.user.role != "officer":
			raise PermissionDenied("Only assigned officers can update complaint status.")

		if complaint.assigned_to != request.user:
			raise PermissionDenied("You can only change the status of complaints assigned to you.")

		if updated_status not in allowed_transitions.get(current_status, []):
			raise ValidationError(
				f"Cannot change status from {current_status} to {updated_status}.")

		complaint.status = updated_status
		complaint.save()

		create_activity_log(
			complaint=complaint,
			user=request.user,
			action=f'Complaint status updated.',
			old_value=current_status,
			new_value=complaint.status,
			)

		return Response({"msg": "Complaint Status Updated.",
			"status": True,
			"body": self.get_serializer(complaint).data
			})

	@action(
		detail=True,
		methods=['get'],
		url_path='history',
		permission_classes=[IsAuthenticated,IsAdminOrReadOnly]
		)
	def complaint_history(self,request,*args,**kwargs):
		complaint = self.get_object()

		activity_log = ActivityLog.objects.filter(complaint=complaint)
		serializer = ActivityLogSerializer(activity_log,many=True)

		return Response ({
		'msg': "Complaint activity log generated.",
		"status": True,
		"result": serializer.data
		})


	@action(
		detail=True,
		methods=['get','post'],
		permission_classes=[IsAuthenticated, IsAuthorOrAssignedOfficer]
		)
	def comment(self,request,*args,**kwargs):
		complaint = self.get_object()
		
		if request.method == 'GET':
			comment = Comment.objects.filter(complaint=complaint)
			serializer = CommentSerializer(comment, many=True)
			return Response ({
			'msg': "Comment for this complaint retreaved successfully.",
			'status': True,
			'body': serializer.data
			})

		elif request.method == 'POST':
			serializer = CommentSerializer(data=request.data)
			serializer.is_valid(raise_exception=True)
			created_comment = serializer.save(complaint=complaint,user=request.user)

			create_activity_log(
			complaint=complaint,
			user=request.user,
			action=f'Comment on a complaint.',
			old_value="",
			new_value=created_comment.message,
			)

			return Response (serializer.data, status=201)
	
	@action(
		detail=True,
		methods=['get', 'post'],
		permission_classes=[IsAuthenticated, IsAuthorOrAssignedOfficer]
		)
	def attachment(self,request,*args,**kwargs):
		complaint= self.get_object()

		if request.method == "GET":
			attachment = Attachment.objects.filter(complaint=complaint)
			serializer= AttachmentSerializer(attachment,many=True)
			return Response ({
			'msg': 'Attachment retreaved successfully.',
			'status': True,
			'body': serializer.data
			})

		elif request.method == "POST":
			serializer = AttachmentSerializer(data=request.data)
			serializer.is_valid(raise_exception=True)
			created_attachment = serializer.save(complaint=complaint, uploaded_by=request.user)

			create_activity_log(
			complaint=complaint,
			user=request.user,
			action=f'Attachment added.',
			old_value="",
			new_value=created_attachment.file.name,
			)

			return Response (serializer.data, status=201)

	@action(
		detail=False,
		methods=['get'],
		permission_classes=[IsAuthenticated, IsAdminOrReadOnly]
		)
	def statistics(self, request, *args, **kwargs):
		total_complaints = Complaint.objects.count()
		submitted_complaints = Complaint.objects.filter(status=Complaint.Status.SUBMITTED).count()
		in_progress_complaints = Complaint.objects.filter(status=Complaint.Status.IN_PROGRESS).count()
		resolved_complaints = Complaint.objects.filter(status=Complaint.Status.RESOLVED).count()
		priority_statistics = {}
		priorities = ['low', 'medium', 'high', 'urgent']

		for priority in priorities:
			priority_statistics[priority] = Complaint.objects.filter(priority=priority).count()

		return Response ({
		'msg': "Complaint Statistics generated.",
		"status": True,
		"body": {
		'total_complaints': total_complaints,
		'submitted_complaints': submitted_complaints,
		'in_progress_complaints': in_progress_complaints,
		'resolved_complaints': resolved_complaints,
		'priority_statistics': priority_statistics
		}
		})