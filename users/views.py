from django.conf import settings
from django.contrib.auth import views as auth_views
from django.core.cache import cache
from django.shortcuts import render

from core.utils import get_client_ip
from dashboard.services import log_action


class ThrottledLoginView(auth_views.LoginView):
    """Login + IP bo'yicha brute-force himoyasi."""

    template_name = "login.html"
    redirect_authenticated_user = True

    def _key(self):
        return f"login-fail:{get_client_ip(self.request)}"

    def post(self, request, *args, **kwargs):
        if cache.get(self._key(), 0) >= settings.LOGIN_MAX_ATTEMPTS:
            form = self.get_form()
            form.add_error(None, "Too many failed attempts. Try again in 15 minutes.")
            return render(request, self.template_name, {"form": form}, status=429)
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        key = self._key()
        cache.set(key, cache.get(key, 0) + 1, settings.LOGIN_LOCKOUT_SECONDS)
        return super().form_invalid(form)

    def form_valid(self, form):
        cache.delete(self._key())
        response = super().form_valid(form)
        if self.request.user.is_dashboard_user:
            log_action(self.request, "logged in", "dashboard")
        return response

    def get_success_url(self):
        url = self.get_redirect_url()
        if url:
            return url
        return "/dashboard/" if self.request.user.is_dashboard_user else "/"
