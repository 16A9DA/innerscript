import logging

from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings

from config.permissions import is_admin
from .forms import ProfileForm
from .models import Profile
from .workos_client import workos_client

User = get_user_model()
logger = logging.getLogger(__name__)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.select_related("category")
    if request.user != user:
        posts = posts.filter(is_public=True)
    return render(request, "accounts/profile.html", {
        "profile_user": user,
        "posts": posts,
        "is_admin": is_admin(request.user),
    })


@login_required
def profile_edit(request):
    prof = request.user.profile
    form = ProfileForm(request.POST or None, request.FILES or None, instance=prof)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("accounts:profile", username=form.cleaned_data["username"])
    return render(request, "accounts/profile_edit.html", {"form": form})


@login_required
def account_delete(request):
    """Self-service account deletion. Removes the user and, by cascade, their
    profile, posts, comments, likes. Also best-effort deletes the linked
    WorkOS user so no record survives on either side. No soft-delete, no
    retention."""
    if request.method == "POST":
        user = request.user
        workos_user_id = user.profile.workos_user_id
        if workos_user_id:
            try:
                workos_client.user_management.delete_user(workos_user_id)
            except Exception:
                logger.exception("WorkOS delete_user failed for %s", workos_user_id)
        logout(request)
        user.delete()
        return redirect("pages:home")
    return render(request, "accounts/account_delete.html")


@login_required
def admin_user_delete(request, username):
    """Admin-only. Self-delete stays on the account_delete route."""
    if not is_admin(request.user):
        raise PermissionDenied
    target = get_object_or_404(User, username=username)
    if target == request.user:
        raise PermissionDenied
    if request.method == "POST":
        target.delete()
        return redirect("community:feed")
    return render(request, "accounts/user_confirm_delete.html", {"target": target})


def _unique_username_from_email(email):
    base = email.split("@")[0] or "user"
    username = base
    suffix = 1
    while User.objects.filter(username__iexact=username).exists():
        suffix += 1
        username = f"{base}{suffix}"
    return username


def workos_start(request, screen_hint):
    url = workos_client.user_management.get_authorization_url(
        provider="authkit",
        redirect_uri=settings.WORKOS_REDIRECT_URI,
        screen_hint=screen_hint,
    )
    return redirect(url)


def workos_callback(request):
    code = request.GET.get("code")
    auth_response = workos_client.user_management.authenticate_with_code(code=code)
    wos_user = auth_response.user

    try:
        profile = Profile.objects.get(workos_user_id=wos_user.id)
        user = profile.user
    except Profile.DoesNotExist:
        user = None
        if wos_user.email_verified:
            user = User.objects.filter(email__iexact=wos_user.email).first()
        if user is None:
            user = User.objects.create(
                username=_unique_username_from_email(wos_user.email),
                email=wos_user.email,
                first_name=wos_user.first_name or "",
                last_name=wos_user.last_name or "",
            )
            user.set_unusable_password()
            user.save(update_fields=["password"])
        user.profile.workos_user_id = wos_user.id
        user.profile.save(update_fields=["workos_user_id"])

    site_role = (wos_user.metadata or {}).get("site_role", "")
    if site_role != user.profile.site_role:
        user.profile.site_role = site_role
        user.profile.save(update_fields=["site_role"])

    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    if not user.profile.role:
        return redirect("accounts:profile_edit")
    return redirect(settings.LOGIN_REDIRECT_URL)


def workos_logout_view(request):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)
