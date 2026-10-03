from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from portfolio.sitemaps import ProjectSitemap, StaticSitemap

# Django admin faqat superuser uchun
admin.site.has_permission = lambda request: request.user.is_active and request.user.is_superuser

sitemaps = {"static": StaticSitemap, "projects": ProjectSitemap}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("users.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path("", include("portfolio.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
