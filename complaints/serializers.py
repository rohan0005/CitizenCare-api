from rest_framework import serializers
from .models import Complaint, Department, Category, ActivityLog

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
