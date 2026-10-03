from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render

from core.utils import get_client_ip

from .forms import ContactForm, new_token
from .models import Experience, Project, Service, Skill, Stat

CONTACT_LIMIT = 3  # bir IP dan soatiga


def home(request):
    projects = Project.objects.filter(featured=True)[:3] or Project.objects.all()[:3]
    return render(request, "home.html", {
        "projects": projects,
        "services": Service.objects.all(),
        "stats": Stat.objects.all(),
    })


def about(request):
    skills = {}
    for skill in Skill.objects.all():
        skills.setdefault(skill.get_category_display(), []).append(skill)
    return render(request, "about.html", {
        "skills": skills,
        "experiences": Experience.objects.all(),
        "stats": Stat.objects.all(),
    })


def project_list(request):
    return render(request, "projects.html", {"projects": Project.objects.all()})


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, "project_detail.html", {"project": project})


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        ip = get_client_ip(request)
        key = f"contact:{ip}"
        if cache.get(key, 0) >= CONTACT_LIMIT:
            messages.error(request, "You've sent several messages recently. Please try again later.")
        elif form.is_valid():
            entry = form.save(commit=False)
            entry.ip_address = ip
            entry.save()
            cache.set(key, cache.get(key, 0) + 1, 3600)
            messages.success(request, "Message sent. I'll reply by email.")
            return redirect("portfolio:contact")
    else:
        form = ContactForm(initial={"token": new_token()})
    return render(request, "contact.html", {"form": form})
