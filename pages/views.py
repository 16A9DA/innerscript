from django.shortcuts import render

from community.models import Post
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
    return render(request, "pages/toolkits.html", {"toolkits": Toolkit.objects.all()})


def impact(request):
    return render(request, "pages/impact.html")


def about(request):
    return render(request, "pages/about.html")


def privacy(request):
    return render(request, "pages/privacy.html")
