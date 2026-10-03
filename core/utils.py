from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageOps


def get_client_ip(request):
    """Railway/proxy orqasida haqiqiy IP manzilni oladi."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def optimize_image(field, max_side=1600, quality=82):
    """Yangi yuklangan rasmni kichraytirib, WEBP formatiga o'tkazadi."""
    if not field or getattr(field, "_committed", True):
        return
    try:
        img = ImageOps.exif_transpose(Image.open(field.file))
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if "transparency" in img.info else "RGB")
        img.thumbnail((max_side, max_side))
        buffer = BytesIO()
        img.save(buffer, "WEBP", quality=quality)
    except Exception:
        return  # Rasm bo'lmasa yoki buzilgan bo'lsa, asl fayl qoladi
    field.save(Path(field.name).stem + ".webp", ContentFile(buffer.getvalue()), save=False)
