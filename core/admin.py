from django.contrib import admin

from .models import SiteSettings, SocialLink

admin.site.register(SiteSettings)
admin.site.register(SocialLink)
