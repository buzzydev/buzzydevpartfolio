from django.contrib import admin

from .models import ContactMessage, Experience, Project, Service, Skill, Stat


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "featured", "created_at")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "is_read", "created_at")
    list_filter = ("is_read",)


admin.site.register([Skill, Service, Experience, Stat])
