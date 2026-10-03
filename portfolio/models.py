from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from core.models import OptimizedImageMixin


def split_csv(value):
    return [item.strip() for item in value.split(",") if item.strip()]


class Stat(models.Model):
    label = models.CharField(max_length=60)
    value = models.PositiveIntegerField()
    suffix = models.CharField(max_length=5, blank=True, help_text="Masalan: +")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.label}: {self.value}"


class Skill(models.Model):
    class Category(models.TextChoices):
        FRONTEND = "frontend", "Frontend"
        BACKEND = "backend", "Backend"
        DATABASE = "database", "Database"
        DEVOPS = "devops", "DevOps"
        TOOLS = "tools", "Tools"
        OTHER = "other", "Other"

    name = models.CharField(max_length=60)
    icon = models.CharField(max_length=60, blank=True, help_text="Font Awesome class, masalan: fa-brands fa-python")
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    level = models.PositiveSmallIntegerField(default=70, help_text="0 dan 100 gacha")
    description = models.CharField(max_length=200, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["category", "order", "name"]

    def __str__(self):
        return self.name


class Service(models.Model):
    icon = models.CharField(max_length=60, default="fa-solid fa-code", help_text="Font Awesome class")
    title = models.CharField(max_length=80)
    description = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class Experience(models.Model):
    company = models.CharField(max_length=120)
    position = models.CharField(max_length=120)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Bo'sh qoldirilsa — hozirgacha")
    description = models.TextField(blank=True)
    technologies = models.CharField(max_length=255, blank=True, help_text="Vergul bilan ajrating")

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.position} @ {self.company}"

    @property
    def tech_list(self):
        return split_csv(self.technologies)


class Project(OptimizedImageMixin):
    optimized_fields = ("image",)

    title = models.CharField(max_length=140)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    short_description = models.CharField(max_length=255)
    full_description = models.TextField()
    image = models.ImageField(upload_to="projects/", blank=True)
    technologies = models.CharField(max_length=255, blank=True, help_text="Vergul bilan ajrating")
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["featured", "-created_at"])]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "project"
            slug, n = base, 2
            while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("portfolio:project_detail", args=[self.slug])

    @property
    def tech_list(self):
        return split_csv(self.technologies)


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField(max_length=3000)
    is_read = models.BooleanField(default=False, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}: {self.subject}"
