from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):
		if request.method in permissions.SAFE_METHODS:
			return True

		if request.method == "DELETE":
			return False

		return obj.citizen == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return True
		return request.user.role == "admin"

class IsAdminOfficerOrReadOnly(permissions.BasePermission):
	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return request.user.is_authenticated and request.user.role in ["admin", "officer"]
		return request.user.is_authenticated and request.user.role == "admin"

class IsAuthorOrAssignedOfficer(permissions.BasePermission):
	def has_object_permission(self,request,view,obj):
		complaint = obj

		if request.method in permissions.SAFE_METHODS:
			return (
			request.user.role == "admin" or
			complaint.citizen == request.user or 
			complaint.assigned_to == request.user
			)

		if request.method == 'POST':
			return (
			complaint.citizen == request.user or 
			complaint.assigned_to == request.user
			)

		return False
