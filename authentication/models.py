from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('donor', 'Donor'),
        ('consumer', 'Consumer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)