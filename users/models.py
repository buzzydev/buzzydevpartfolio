from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import OptimizedImageMixin


class User(OptimizedImageMixin, AbstractUser):
    """Custom User. `role` — admin rank (0 = oddiy foydalanuvchi)."""

    class Role(models.IntegerChoices):
        USER = 0, "User"
        MODERATOR = 1, "Moderator"
        EDITOR = 2, "Editor"
        MANAGER = 3, "Manager"
        ADMINISTRATOR = 4, "Administrator"
        SUPER_ADMIN = 5, "Super Administrator"

    optimized_fields = ("profile_picture",)

    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to="avatars/", blank=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    location = models.CharField(max_length=120, blank=True)
    role = models.PositiveSmallIntegerField(choices=Role.choices, default=Role.USER, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Super Administrator faqat Django superuser bo'la oladi
        if self.is_superuser:
            self.role = self.Role.SUPER_ADMIN
            self.is_staff = True
        else:
            if self.role == self.Role.SUPER_ADMIN:
                self.role = self.Role.ADMINISTRATOR
            self.is_staff = self.role >= self.Role.MODERATOR
        super().save(*args, **kwargs)

    @property
    def is_dashboard_user(self):
        return self.is_active and self.is_staff and self.role >= self.Role.MODERATOR
