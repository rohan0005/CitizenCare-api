from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):

	class Role(models.TextChoices):
		CITIZEN= "citizen", "Citizen"
		OFFICER = "officer", "Officer"
		ADMIN = "admin", "Admin"

	role = models.CharField(max_length=20, choices=Role.choices, default=Role.CITIZEN)
	phone_number = models.CharField(max_length=20, blank=True)

	def __str__(self):
		return self.username