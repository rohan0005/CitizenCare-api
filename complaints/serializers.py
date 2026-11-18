from rest_framework import serializers
from .models import Complaint, Department, Category, ActivityLog, Comment, Attachment
import os
from PIL import Image, UnidentifiedImageError

class DepartmentSerializer(serializers.ModelSerializer):
	class Meta:
		model= Department
		fields = "__all__"
		read_only_fields = ["created_at", "updated_at"]

class CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model= Category
		fields = "__all__"
		read_only_fields = ["created_at", "updated_at"]


class ComplaintSerializer(serializers.ModelSerializer):
	class Meta:
		model = Complaint
		fields = ["tracking_id", "title", "description", "category", "citizen", "assigned_to", 
		"status", "remarks", "priority", "location", "created_at", "updated_at", "resolved_at"]

		read_only_fields = ["tracking_id", "status", "assigned_to", "citizen", "created_at",
		"updated_at", "resolved_at",]

	def validate(self,attrs):
		title = attrs.get('title', "" ).strip().lower()
		description = attrs.get('description', "" ).strip().lower()


		if title == description:
			raise serializers.ValidationError('Title and description must not be same.')
		return attrs


class ActivityLogSerializer(serializers.ModelSerializer):
	class Meta:
		model = ActivityLog
		fields = "__all__"
		read_only_fields =["id","complaint","user","action","old_value","new_value","created_at",]


class CommentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Comment
		fields = "__all__"
		read_only_fields = ['id', 'created_at', 'uploaded_at', 'complaint', 'user']

class AttachmentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Attachment
		fields= ['id', 'complaint', 'file', 'uploaded_by', 'uploaded_at']
		read_only_fields = ['id', 'complaint', 'uploaded_by', 'uploaded_at']

	def validate_file(self, value):
		if value.size == 0:
			raise serializers.ValidationError("Empty files are not allowed.")

		if value.size > 5 * 1024 * 1024:
			raise serializers.ValidationError("File size cannot exceed 5 MB.")

		filename = value.name
		ext = os.path.splitext(filename)[1].lower()

		if ext not in ['.png', '.jpg', '.jpeg']:
			raise serializers.ValidationError("Only PNG and JPG images are allowed.")

		try:
			value.seek(0)
			image= Image.open(value)
			image.verify()
			value.seek(0)
			return value
		except (UnidentifiedImageError, OSError):
			raise serializers.ValidationError("Uploaded file is not a valid image.")