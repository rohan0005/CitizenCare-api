from django.db import models
from django.conf import settings

# Create your models here.
class Department(models.Model):
	name = models.CharField(max_length=100,unique=True)
	description= models.TextField(blank=True)
	is_active= models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name

class Category(models.Model):
	name = models.CharField(max_length=100)
	department = models.ForeignKey(Department, on_delete=models.PROTECT,related_name="categories")
	description = models.TextField(blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	unique_together = ("name", "department")

	def __str__(self):
		return f"{self.name} - {self.department.name}"


class Complaint(models.Model):

	class Status(models.TextChoices):
		PENDING = "pending", "Pending"
		ASSIGNED = "assigned", "Assigned"
		IN_PROGRESS = "in_progress", "In Progress"
		RESOLVED = "resolved", "Resolved"
		CLOSED = "closed", "Closed"
		REJECTED = "rejected", "Rejected"

	class Priority(models.TextChoices):
		LOW = "low", "Low"
		MEDIUM = "medium", "Medium"
		HIGH = "high", "High"
		URGENT = "urgent", "Urgent"

	tracking_id = models.CharField(max_length=30, unique=True)
	title = models.CharField(max_length=200)
	description = models.TextField()
	category = models.ForeignKey("Category", on_delete=models.PROTECT, related_name="complaints")
	citizen = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="submitted_complaints")
	assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="assigned_complaints", null=True, blank=True)
	status = models.CharField(max_length=20,choices=Status.choices,default=Status.PENDING)
	remarks = models.TextField(blank=True) 
	priority =models.CharField(max_length=10, choices=Priority.choices,default=Priority.MEDIUM) 
	location = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	resolved_at = models.DateTimeField(null=True,blank=True)

	
	def __str__(self):
		return self.title

	class Meta:
		ordering =["-created_at"]
		verbose_name = "Complaint"
		verbose_name_plural = "Complaints"


class Attachment(models.Model):
	complaint = models.ForeignKey("Complaint", on_delete=models.CASCADE, related_name="attachments")
	file= models.FileField(upload_to="complaints/attachments/")
	uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.PROTECT, related_name="uploaded_attachments")
	uploaded_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.complaint.title} - Attachment"


class Comment(models.Model):
	complaint = models.ForeignKey("Complaint", on_delete=models.CASCADE, related_name="comments")
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.PROTECT, related_name="comments")
	message = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Comment by {self.user.username} on {self.complaint.tracking_id}"

	class Meta:
		ordering = ["created_at"]

class ActivityLog(models.Model):
	complaint = models.ForeignKey("Complaint", on_delete=models.CASCADE, related_name="activity_logs")
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, null=True, blank=True,related_name="activity_logs")
	action = models.CharField(max_length=200)
	old_value = models.TextField(blank=True)
	new_value = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.action} - {self.complaint.tracking_id}"

	class Meta:
		ordering = ["created_at"]