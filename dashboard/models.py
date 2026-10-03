from django.conf import settings
from django.db import models


class AdminActionLog(models.Model):
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="action_logs")
    admin_name = models.CharField(max_length=150)  # admin o'chirilsa ham ism qoladi
    action = models.CharField(max_length=80)
    target = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Admin {self.admin_name} {self.action} {self.target}".strip()
