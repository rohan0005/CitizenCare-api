from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from complaints.models import Department, Category,Complaint

User = get_user_model()

# Create your tests here.
class ComplaintAPITestCase(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username="testcitizen",
	        password="testpassword123",
	        role="citizen",
	        phone_number="9800000000",
	        department=None
			)

		self.user2 = User.objects.create_user(
			username="testcitizen2",
	        password="testpassword123",
	        role="citizen",
	        phone_number="9800000002",
	        department=None
			)

		self.department = Department.objects.create(name="Road Department")
		self.category = Category.objects.create(name="Road Damage",department=self.department)

	def test_unauthenticated_user_cannot_access_complaints(self):
		response = self.client.get('/api/complaints/')
		self.assertEqual(response.status_code, 401)

	def test_unauthenticated_user_can_access_complaints(self):
		self.client.force_authenticate(user=self.user)
		response = self.client.get("/api/complaints/")
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_citizen_can_create_complaint(self):
		self.client.force_authenticate(user=self.user)
		data = {'title': 'Bad road', 'description': "fix our road asap", 'category': self.category.id, 
		'priority':'medium','location':'hetauda'}
		response = self.client.post('/api/complaints/', data)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Complaint.objects.count(),1)
		self.assertEqual(Complaint.objects.first().citizen, self.user)

	def test_citizen_must_not_be_able_to_view_another_citizens_complaints(self):
		complaint = Complaint.objects.create(
		    title="Bad road",
		    description="Road needs repair",
		    category=self.category,
		    citizen=self.user
		)

		# Authenticate as Citizen 2
		self.client.force_authenticate(user=self.user2)

		response = self.client.get(f"/api/complaints/{complaint.tracking_id}/",)
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


	def test_citizen_complaint_update_only_when_its_status_is_submitted(self):
		complaint = Complaint.objects.create(
		    title="Bad road",
		    description="Road needs repair",
		    category=self.category,
		    citizen=self.user
		)
		self.client.force_authenticate(user=self.user)

		new_title = "Very bad road condition"

		complaint_tracking_id= complaint.tracking_id

		data = {"title": new_title}

		response = self.client.patch(f"/api/complaints/{complaint_tracking_id}/", data=data,)

		self.assertEqual(response.status_code, status.HTTP_200_OK)

		complaint.refresh_from_db()
		
		self.assertEqual(complaint.title, new_title)


	# def test_citizen_cannot_update_assigned_complaint(self):