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


class ItrUsers(AbstractUser):
    user_id = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='itrusers_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='itrusers_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )
    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.user_id