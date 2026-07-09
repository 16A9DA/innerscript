from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CommentForm, PostForm
from .models import Category, Like, Post


def _safe_next(request, fallback):
    ref = request.META.get("HTTP_REFERER", "")
    if ref and url_has_allowed_host_and_scheme(
        ref, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(ref)
    return redirect(fallback)


def feed(request):
    qs = Post.objects.select_related("author", "category")
    if request.user.is_authenticated:
        qs = qs.filter(Q(is_public=True) | Q(author=request.user))
    else:
        qs = qs.filter(is_public=True)
    posts = list(qs)
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
        "active_category": Category.objects.filter(slug=cat).first() if cat else None,
    })


def post_detail(request, slug):
    post = get_object_or_404(Post.objects.select_related("author", "category"), slug=slug)
    if not post.is_public and post.author != request.user:
        raise Http404
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
    return _safe_next(request, post.get_absolute_url())


@require_POST
@login_required
def visibility_toggle(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    post.is_public = not post.is_public
    post.save(update_fields=["is_public"])
    return _safe_next(request, post.get_absolute_url())
