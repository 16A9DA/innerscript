from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from community.models import Post
from config.permissions import can_delete_toolkit, is_member
from .forms import ToolkitForm
from .models import Toolkit


def home(request):
    posts = sorted(
        Post.objects.select_related("author", "category"),
        key=lambda p: p.community_score,
        reverse=True,
    )[:4]
    return render(request, "pages/home.html", {"posts": posts})


def initiatives(request):
    return render(request, "pages/initiatives.html")


def toolkits(request):
    member = is_member(request.user)
    if member:
        pending = Toolkit.objects.filter(is_approved=False)
    elif request.user.is_authenticated:
        pending = Toolkit.objects.filter(is_approved=False, uploaded_by=request.user)
    else:
        pending = None
    return render(request, "pages/toolkits.html", {
        "toolkits": Toolkit.objects.filter(is_approved=True),
        "pending": pending,
        "can_upload": request.user.is_authenticated,
        "can_moderate": member,
    })


@login_required
def toolkit_upload(request):
    """Any signed-in user may submit a toolkit; it stays pending until a member/admin approves it."""
    form = ToolkitForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        toolkit = form.save(commit=False)
        toolkit.uploaded_by = request.user
        toolkit.save()
        messages.success(request, "Submitted for review.")
        return redirect("pages:toolkits")
    return render(request, "pages/toolkit_form.html", {"form": form})


@require_POST
@login_required
def toolkit_approve(request, pk):
    if not is_member(request.user):
        raise PermissionDenied
    toolkit = get_object_or_404(Toolkit, pk=pk)
    toolkit.is_approved = True
    toolkit.save(update_fields=["is_approved"])
    return redirect("pages:toolkits")


@login_required
def toolkit_delete(request, pk):
    """Owner or member. No soft-delete, no retention."""
    toolkit = get_object_or_404(Toolkit, pk=pk)
    if not can_delete_toolkit(request.user, toolkit):
        raise PermissionDenied
    if request.method == "POST":
        toolkit.delete()
        return redirect("pages:toolkits")
    return render(request, "pages/toolkit_confirm_delete.html", {"toolkit": toolkit})


def impact(request):
    return render(request, "pages/impact.html")


def about(request):
    return render(request, "pages/about.html")


def privacy(request):
    return render(request, "pages/privacy.html")
