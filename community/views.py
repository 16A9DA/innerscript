from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CommentForm, PostForm
from .models import Category, Like, Post


def feed(request):
    posts = list(Post.objects.select_related("author", "category"))
    sort = request.GET.get("sort", "score")
    cat = request.GET.get("cat")
    if cat:
        posts = [p for p in posts if p.category and p.category.slug == cat]
    if sort == "recent":
        posts.sort(key=lambda p: p.created, reverse=True)
    elif sort == "discussed":
        posts.sort(key=lambda p: p.comment_count, reverse=True)
    else:
        posts.sort(key=lambda p: p.community_score, reverse=True)
    featured = posts[0] if posts else None
    rest = posts[1:] if posts else []
    return render(request, "community/feed.html", {
        "featured": featured,
        "posts": rest,
        "categories": Category.objects.all(),
        "sort": sort,
        "active_cat": cat,
    })


def post_detail(request, slug):
    post = get_object_or_404(Post.objects.select_related("author", "category"), slug=slug)
    form = CommentForm(request.POST or None)
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("account_login")
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect(post.get_absolute_url())
    liked = (
        request.user.is_authenticated
        and post.likes.filter(user=request.user).exists()
    )
    return render(request, "community/post_detail.html", {
        "post": post,
        "comments": post.comments.select_related("author"),
        "form": form,
        "liked": liked,
    })


@login_required
def post_create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(post.get_absolute_url())
    return render(request, "community/post_form.html", {"form": form})


@require_POST
@login_required
def like_toggle(request, slug):
    post = get_object_or_404(Post, slug=slug)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    # Only follow the referer if it is same-origin, else it is an open redirect.
    referer = request.META.get("HTTP_REFERER", "")
    if referer and url_has_allowed_host_and_scheme(
        referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(referer)
    return redirect(post.get_absolute_url())
