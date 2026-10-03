from .permissions import has_access

NAV = [
    ("Dashboard", "dashboard:index", "dashboard", "fa-solid fa-gauge"),
    ("Projects", "dashboard:projects_list", "projects", "fa-solid fa-folder-open"),
    ("Skills", "dashboard:skills_list", "skills", "fa-solid fa-star"),
    ("Services", "dashboard:services_list", "services", "fa-solid fa-briefcase"),
    ("Experience", "dashboard:experience_list", "experience", "fa-solid fa-timeline"),
    ("Stats", "dashboard:stats_list", "stats", "fa-solid fa-chart-simple"),
    ("Social links", "dashboard:social_list", "social", "fa-solid fa-share-nodes"),
    ("Messages", "dashboard:messages", "messages", "fa-solid fa-envelope"),
    ("Users", "dashboard:users", "users", "fa-solid fa-users"),
    ("Admins", "dashboard:admins", "admins", "fa-solid fa-user-shield"),
    ("Settings", "dashboard:settings", "settings", "fa-solid fa-gear"),
    ("Action logs", "dashboard:logs", "logs", "fa-solid fa-clock-rotate-left"),
]


def dashboard_nav(request):
    if not request.path.startswith("/dashboard/"):
        return {}
    return {"dash_nav": [item for item in NAV if has_access(request.user, item[2])]}
