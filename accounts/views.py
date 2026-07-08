from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileForm

User = get_user_model()


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.select_related("category")
    if request.user != user:
        posts = posts.filter(is_public=True)
    return render(request, "accounts/profile.html", {
        "profile_user": user,
        "posts": posts,
    })


@login_required
def profile_edit(request):
    prof = request.user.profile
    form = ProfileForm(request.POST or None, request.FILES or None, instance=prof)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("accounts:profile", username=request.user.username)
    return render(request, "accounts/profile_edit.html", {"form": form})


@login_required
def account_delete(request):
    """Self-service account deletion. Removes the user and, by cascade, their
    profile, posts, comments, likes, and social account. No soft-delete, no
    retention."""
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        return redirect("pages:home")
    return render(request, "accounts/account_delete.html")
