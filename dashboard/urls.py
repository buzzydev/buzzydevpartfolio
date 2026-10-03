from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    path("messages/", views.message_list, name="messages"),
    path("messages/<int:pk>/", views.message_detail, name="message_detail"),
    path("messages/<int:pk>/toggle/", views.message_toggle, name="message_toggle"),
    path("messages/<int:pk>/delete/", views.message_delete, name="message_delete"),
    path("users/", views.user_list, name="users"),
    path("users/<int:pk>/toggle/", views.user_toggle, name="user_toggle"),
    path("admins/", views.admin_list, name="admins"),
    path("admins/new/", views.admin_create, name="admin_create"),
    path("admins/<int:pk>/rank/", views.admin_rank, name="admin_rank"),
    path("settings/", views.site_settings, name="settings"),
    path("logs/", views.logs, name="logs"),
]

for _key in views.CRUD:
    urlpatterns += [
        path(f"{_key}/", views.crud_list, {"key": _key}, name=f"{_key}_list"),
        path(f"{_key}/new/", views.crud_edit, {"key": _key}, name=f"{_key}_create"),
        path(f"{_key}/<int:pk>/edit/", views.crud_edit, {"key": _key}, name=f"{_key}_edit"),
        path(f"{_key}/<int:pk>/delete/", views.crud_delete, {"key": _key}, name=f"{_key}_delete"),
    ]
