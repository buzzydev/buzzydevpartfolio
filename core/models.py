from django.db import models

from .utils import optimize_image


class OptimizedImageMixin(models.Model):
    """optimized_fields ichidagi rasmlar saqlashdan oldin optimallashtiriladi."""

    optimized_fields = ()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        for name in self.optimized_fields:
            optimize_image(getattr(self, name))
        super().save(*args, **kwargs)


class SiteSettings(OptimizedImageMixin):
    """Yagona (singleton) yozuv: sayt sozlamalari."""

    optimized_fields = ("profile_image",)

    website_title = models.CharField(max_length=120, default="BuzzyDev")
    website_description = models.CharField(max_length=255, blank=True)
    profile_name = models.CharField(max_length=120, default="BuzzyDev")
    profile_title = models.CharField(max_length=120, default="Full-Stack Developer")
    hero_text = models.CharField(
        max_length=255, default="Building modern, scalable and high-performance web applications."
    )
    profile_image = models.ImageField(upload_to="profile/", blank=True)
    about_text = models.TextField(blank=True)
    education = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    location = models.CharField(max_length=120, blank=True)
    github = models.URLField(blank=True)
    telegram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    favicon = models.ImageField(upload_to="profile/", blank=True)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return self.website_title

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SocialLink(models.Model):
    PLATFORMS = {
        "github": ("GitHub", "fa-brands fa-github"),
        "telegram": ("Telegram", "fa-brands fa-telegram"),
        "instagram": ("Instagram", "fa-brands fa-instagram"),
        "linkedin": ("LinkedIn", "fa-brands fa-linkedin"),
        "discord": ("Discord", "fa-brands fa-discord"),
        "youtube": ("YouTube", "fa-brands fa-youtube"),
        "x": ("X / Twitter", "fa-brands fa-x-twitter"),
        "other": ("Other", "fa-solid fa-link"),
    }

    platform = models.CharField(max_length=20, choices=[(k, v[0]) for k, v in PLATFORMS.items()])
    url = models.URLField()
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.get_platform_display()

    @property
    def icon(self):
        return self.PLATFORMS[self.platform][1]
