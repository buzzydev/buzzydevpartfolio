from .models import SiteSettings, SocialLink


def site(request):
    settings_obj = SiteSettings.load()
    links = list(SocialLink.objects.filter(is_active=True))
    if not links:  # Social link kiritilmagan bo'lsa, sozlamalardagi linklar ishlatiladi
        for key in ("github", "telegram", "linkedin", "instagram"):
            url = getattr(settings_obj, key)
            if url:
                links.append(SocialLink(platform=key, url=url))
    return {"site_cfg": settings_obj, "social_links": links}
