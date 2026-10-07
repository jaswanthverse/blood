from django.contrib.auth.models import AbstractUser
from django.db import models


class StaffUser(AbstractUser):
    """
    Extends Django's built-in User with a role field.

    ADMIN - full access: add/edit/delete units, manage staff
    STAFF - day-to-day work: add units, reserve, issue
    """

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        STAFF = 'STAFF', 'Staff'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STAFF)
    phone_number = models.CharField(max_length=15, blank=True)

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"