from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('ca', 'Chartered Accountant'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    assigned_ca = models.ForeignKey('self', null=True, blank=True, limit_choices_to={'role': 'ca'}, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.username} ({self.role})"
