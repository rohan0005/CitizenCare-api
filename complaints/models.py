from django.db import models

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


# class Complaint(models.Model):
	
	