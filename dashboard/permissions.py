from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

# Bo'lim -> kerakli minimal rank
SECTION_RANK = {
    "dashboard": 1,
    "messages": 1,
    "message_delete": 2,
    "projects": 2,
    "skills": 2,
    "services": 2,
    "experience": 2,
    "stats": 2,
    "social": 2,
    "users": 3,
    "admins": 4,
    "settings": 4,
    "logs": 4,
}


def has_access(user, section):
    return user.is_authenticated and user.is_dashboard_user and user.role >= SECTION_RANK[section]


def check_access(request, section):
    if not has_access(request.user, section):
        raise PermissionDenied


def rank_required(section):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(request, *args, **kwargs):
            check_access(request, section)
            return view(request, *args, **kwargs)

        return wrapper

    return decorator


def can_manage_user(actor, target):
    """Actor target foydalanuvchini faolsizlantira/faollashtira oladimi."""
    if actor.pk == target.pk:
        return False
    if actor.is_superuser:
        return True
    if actor.role >= 4:
        return target.role < 4
    if actor.role >= 3:
        return target.role == 0
    return False
