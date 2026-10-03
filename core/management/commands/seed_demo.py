from datetime import date

from django.core.management.base import BaseCommand

from core.models import SiteSettings, SocialLink
from portfolio.models import Experience, Project, Service, Skill, Stat


class Command(BaseCommand):
    help = "Namuna ma'lumotlar bilan saytni to'ldiradi (faqat bo'sh bo'lsa)."

    def handle(self, *args, **options):
        s = SiteSettings.load()
        if not s.about_text:
            s.website_description = "Portfolio of BuzzyDev: web applications, APIs and Telegram bots."
            s.about_text = "I build web applications and Telegram bots with Python and Django, from database design to deployment."
            s.location = "Tashkent, Uzbekistan"
            s.seo_title = "BuzzyDev — Full-Stack Developer"
            s.seo_description = "Full-Stack Developer building Django web apps, APIs and Telegram bots."
            s.save()
        if not Stat.objects.exists():
            for i, (label, value, suffix) in enumerate([("Years of experience", 3, "+"), ("Projects completed", 20, "+"), ("Clients", 8, "+"), ("Technologies", 15, "+")]):
                Stat.objects.create(label=label, value=value, suffix=suffix, order=i)
        if not Skill.objects.exists():
            for name, icon, cat, level in [
                ("HTML & CSS", "fa-brands fa-html5", "frontend", 85), ("JavaScript", "fa-brands fa-js", "frontend", 75),
                ("Python", "fa-brands fa-python", "backend", 90), ("Django", "fa-solid fa-server", "backend", 88),
                ("PostgreSQL", "fa-solid fa-database", "database", 80), ("Railway", "fa-solid fa-train", "devops", 75),
                ("Git & GitHub", "fa-brands fa-github", "tools", 85),
            ]:
                Skill.objects.create(name=name, icon=icon, category=cat, level=level)
        if not Service.objects.exists():
            for icon, title, text in [
                ("fa-solid fa-globe", "Web development", "Fast, responsive websites and web apps built with Django."),
                ("fa-solid fa-server", "Backend and APIs", "Clean REST APIs, authentication and business logic."),
                ("fa-brands fa-telegram", "Telegram bots", "Bots with catalogs, payments and admin panels."),
                ("fa-solid fa-database", "Database design", "Schemas, migrations and query optimisation for PostgreSQL."),
                ("fa-solid fa-rocket", "Deployment", "Railway and GitHub pipelines with automatic deploys."),
                ("fa-solid fa-pen-ruler", "UI/UX development", "Interfaces that feel simple on desktop and mobile."),
            ]:
                Service.objects.create(icon=icon, title=title, description=text)
        if not Experience.objects.exists():
            Experience.objects.create(company="Freelance", position="Full-Stack Developer", start_date=date(2023, 1, 1),
                                      description="Web apps and Telegram bots for small businesses.", technologies="Python, Django, aiogram, PostgreSQL")
        if not Project.objects.exists():
            Project.objects.create(title="Telegram Media Bot", short_description="Uzbek Telegram bot with a movie and anime catalog.",
                                   full_description="A bot with a searchable catalog and role-based admin tools.", technologies="Python, aiogram, SQLite", featured=True)
        if not SocialLink.objects.exists():
            SocialLink.objects.create(platform="github", url="https://github.com/", order=0)
            SocialLink.objects.create(platform="telegram", url="https://t.me/buzzybro", order=1)
        self.stdout.write(self.style.SUCCESS("Demo content added."))
