from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Project


class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return ["portfolio:home", "portfolio:about", "portfolio:projects", "portfolio:contact"]

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Project.objects.all()

    def lastmod(self, obj):
        return obj.updated_at
