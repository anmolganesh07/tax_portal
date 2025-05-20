from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('ca', 'Chartered Accountant'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    assigned_ca = models.ForeignKey('self', null=True, blank=True, limit_choices_to={'role': 'ca'}, on_delete=models.SET_NULL)
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    aadhar_number = models.CharField(max_length=12, blank=True, null=True)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    bank_account = models.CharField(max_length=20, blank=True, null=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.pan_number and len(self.pan_number) < 10:
            raise ValidationError({'pan_number': 'PAN number must be at least 10 characters.'})
        if self.aadhar_number and len(self.aadhar_number) < 12:
            raise ValidationError({'aadhar_number': 'Aadhar number must be at least 12 characters.'})
        if self.phone_number and len(self.phone_number) < 10:
            raise ValidationError({'phone_number': 'Phone number must be at least 10 digits.'})
        if self.bank_account and len(self.bank_account) < 10:
            raise ValidationError({'bank_account': 'Bank account number must be at least 9 digits.'})
    
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