"""URL configuration for config project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from accounts import views as accounts_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", accounts_views.workos_start, {"screen_hint": "sign-in"}, name="account_login"),
    path("accounts/signup/", accounts_views.workos_start, {"screen_hint": "sign-up"}, name="account_signup"),
    path("accounts/logout/", accounts_views.workos_logout_view, name="account_logout"),
    path("accounts/callback/", accounts_views.workos_callback, name="workos_callback"),
    path("u/", include("accounts.urls")),
    path("community/", include("community.urls")),
    path("", include("pages.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
