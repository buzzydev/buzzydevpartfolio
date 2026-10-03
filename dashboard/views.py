import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from core.models import SiteSettings, SocialLink
from portfolio.models import ContactMessage, Experience, Project, Service, Skill, Stat

from .forms import AdminCreateForm, RankForm, make_form, style_form
from .models import AdminActionLog
from .permissions import can_manage_user, check_access, rank_required
from .services import log_action

User = get_user_model()

CRUD = {
    "projects": dict(model=Project, label="Project", cols=[("Title", "title"), ("Featured", "featured"), ("Created", "created_at")],
                     fields=["title", "slug", "short_description", "full_description", "image", "technologies", "github_url", "live_url", "featured"]),
    "skills": dict(model=Skill, label="Skill", cols=[("Name", "name"), ("Category", "category"), ("Level", "level")],
                   fields=["name", "icon", "category", "level", "description", "order"]),
    "services": dict(model=Service, label="Service", cols=[("Title", "title"), ("Order", "order")],
                     fields=["icon", "title", "description", "order"]),
    "experience": dict(model=Experience, label="Experience", cols=[("Position", "position"), ("Company", "company"), ("Start", "start_date"), ("End", "end_date")],
                       fields=["company", "position", "start_date", "end_date", "description", "technologies"]),
    "stats": dict(model=Stat, label="Stat", cols=[("Label", "label"), ("Value", "value"), ("Order", "order")],
                  fields=["label", "value", "suffix", "order"]),
    "social": dict(model=SocialLink, label="Social link", cols=[("Platform", "platform"), ("URL", "url"), ("Active", "is_active")],
                   fields=["platform", "url", "order", "is_active"]),
}


def _safe_next(request, fallback):
    target = request.POST.get("next", "")
    if url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}):
        return target
    return fallback


def _paginate(request, queryset, per_page=20):
    return Paginator(queryset, per_page).get_page(request.GET.get("page"))


def _display(value):
    if value is None or value == "":
        return "—"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")
    return str(value)


# ---------- Overview ----------

@rank_required("dashboard")
def index(request):
    today = timezone.localdate()
    days = [today - timedelta(days=i) for i in range(13, -1, -1)]
    per_day = dict(ContactMessage.objects.filter(created_at__date__gte=days[0])
                   .annotate(d=TruncDate("created_at")).values("d").annotate(c=Count("id")).values_list("d", "c"))
    per_month = list(Project.objects.annotate(m=TruncMonth("created_at")).values("m").annotate(c=Count("id"))
                     .values_list("m", "c").order_by("m"))[-6:]
    roles = dict(User.objects.values("role").annotate(c=Count("id")).values_list("role", "c"))
    charts = {
        "messages": {"labels": [d.strftime("%d %b") for d in days], "data": [per_day.get(d, 0) for d in days]},
        "projects": {"labels": [m.strftime("%b %Y") for m, _ in per_month], "data": [c for _, c in per_month]},
        "users": {"labels": [label for _, label in User.Role.choices], "data": [roles.get(v, 0) for v, _ in User.Role.choices]},
    }
    return render(request, "dashboard/index.html", {
        "totals": [
            ("Projects", Project.objects.count(), "fa-solid fa-folder-open"),
            ("Skills", Skill.objects.count(), "fa-solid fa-star"),
            ("Messages", ContactMessage.objects.count(), "fa-solid fa-envelope"),
            ("Users", User.objects.count(), "fa-solid fa-users"),
            ("Admins", User.objects.filter(role__gte=1).count(), "fa-solid fa-user-shield"),
        ],
        "unread": ContactMessage.objects.filter(is_read=False).count(),
        "recent": ContactMessage.objects.all()[:5],
        "charts": charts,
    })


# ---------- Generic CRUD ----------

def _cfg(key):
    if key not in CRUD:
        raise Http404
    return CRUD[key]


@login_required
def crud_list(request, key):
    check_access(request, key)
    cfg = _cfg(key)
    page = _paginate(request, cfg["model"].objects.all())
    rows = [(obj, [_display(getattr(obj, attr)) for _, attr in cfg["cols"]]) for obj in page]
    return render(request, "dashboard/list.html", {"key": key, "cfg": cfg, "page": page, "rows": rows,
                                                   "headers": [h for h, _ in cfg["cols"]]})


@login_required
def crud_edit(request, key, pk=None):
    check_access(request, key)
    cfg = _cfg(key)
    obj = get_object_or_404(cfg["model"], pk=pk) if pk else None
    form = make_form(cfg["model"], cfg["fields"], request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        saved = form.save()
        log_action(request, "updated" if obj else "created", f"{cfg['label'].lower()} {saved}")
        messages.success(request, f"{cfg['label']} {'updated' if obj else 'created'}.")
        return redirect(f"dashboard:{key}_list")
    return render(request, "dashboard/form.html", {"form": form, "title": f"{'Edit' if obj else 'New'} {cfg['label'].lower()}",
                                                   "back": f"dashboard:{key}_list"})


@login_required
def crud_delete(request, key, pk):
    check_access(request, key)
    cfg = _cfg(key)
    obj = get_object_or_404(cfg["model"], pk=pk)
    if request.method == "POST":
        log_action(request, "deleted", f"{cfg['label'].lower()} {obj}")
        obj.delete()
        messages.success(request, f"{cfg['label']} deleted.")
        return redirect(f"dashboard:{key}_list")
    return render(request, "dashboard/confirm_delete.html", {"obj": obj, "back": f"dashboard:{key}_list"})


# ---------- Messages ----------

@rank_required("messages")
def message_list(request):
    qs = ContactMessage.objects.all()
    status = request.GET.get("status")
    if status == "unread":
        qs = qs.filter(is_read=False)
    elif status == "read":
        qs = qs.filter(is_read=True)
    return render(request, "dashboard/messages.html", {"page": _paginate(request, qs), "status": status or "all"})


@rank_required("messages")
def message_detail(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    if not msg.is_read:
        msg.is_read = True
        msg.save(update_fields=["is_read"])
    return render(request, "dashboard/message_detail.html", {"msg": msg})


@rank_required("messages")
@require_POST
def message_toggle(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = not msg.is_read
    msg.save(update_fields=["is_read"])
    log_action(request, f"marked message as {'read' if msg.is_read else 'unread'}", msg)
    return redirect(_safe_next(request, "dashboard:messages"))


@rank_required("message_delete")
@require_POST
def message_delete(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    log_action(request, "deleted message", msg)
    msg.delete()
    messages.success(request, "Message deleted.")
    return redirect("dashboard:messages")


# ---------- Users & admins ----------

def _user_rows(request, qs):
    page = _paginate(request, qs, 25)
    return page, [(u, can_manage_user(request.user, u)) for u in page]


@rank_required("users")
def user_list(request):
    qs = User.objects.all()
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(username__icontains=q) | Q(email__icontains=q))
    page, rows = _user_rows(request, qs)
    return render(request, "dashboard/users.html", {"page": page, "rows": rows, "q": q})


@rank_required("users")
@require_POST
def user_toggle(request, pk):
    target = get_object_or_404(User, pk=pk)
    if not can_manage_user(request.user, target):
        raise PermissionDenied
    target.is_active = not target.is_active
    target.save(update_fields=["is_active"])
    log_action(request, "activated user" if target.is_active else "deactivated user", target)
    return redirect(_safe_next(request, "dashboard:users"))


@rank_required("admins")
def admin_list(request):
    page, rows = _user_rows(request, User.objects.filter(role__gte=1))
    return render(request, "dashboard/admins.html", {"page": page, "rows": rows, "roles": RankForm().fields["role"].choices})


@rank_required("admins")
def admin_create(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    form = style_form(AdminCreateForm(request.POST or None))
    if request.method == "POST" and form.is_valid():
        user = form.save()
        log_action(request, f"created admin ({user.get_role_display()})", user)
        messages.success(request, f"Admin {user.username} created.")
        return redirect("dashboard:admins")
    return render(request, "dashboard/form.html", {"form": form, "title": "New admin", "back": "dashboard:admins"})


@rank_required("admins")
@require_POST
def admin_rank(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied  # faqat Super Administrator rank bera oladi
    target = get_object_or_404(User, pk=pk)
    form = RankForm(request.POST)
    if target.pk == request.user.pk or target.is_superuser or not form.is_valid():
        raise PermissionDenied
    old = target.get_role_display()
    target.role = form.cleaned_data["role"]
    target.save()
    log_action(request, f"changed rank {old} -> {target.get_role_display()} for", target)
    messages.success(request, f"{target.username} is now {target.get_role_display()}.")
    return redirect("dashboard:admins")


# ---------- Settings & logs ----------

@rank_required("settings")
def site_settings(request):
    form = make_form(SiteSettings, "__all__", request.POST or None, request.FILES or None, instance=SiteSettings.load())
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "updated", "website settings")
        messages.success(request, "Settings saved.")
        return redirect("dashboard:settings")
    return render(request, "dashboard/form.html", {"form": form, "title": "Website settings", "back": "dashboard:index"})


@rank_required("logs")
def logs(request):
    return render(request, "dashboard/logs.html", {"page": _paginate(request, AdminActionLog.objects.all(), 30)})
