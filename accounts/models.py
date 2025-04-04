from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email_verified = models.BooleanField(default=False)
    campus_email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    home_address = models.CharField(max_length=255, blank=True)
    preferred_pickup_time = models.TimeField(null=True, blank=True)
    preferred_return_time = models.TimeField(null=True, blank=True)
    max_deviation_minutes = models.IntegerField(default=15)  # Maximum acceptable time deviation

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
