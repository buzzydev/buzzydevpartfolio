from core.utils import get_client_ip

from .models import AdminActionLog


def log_action(request, action, target=""):
    AdminActionLog.objects.create(
        admin=request.user,
        admin_name=request.user.username,
        action=action,
        target=str(target)[:255],
        ip_address=get_client_ip(request),
    )
