from django.urls import path

from . import views

app_name = "community"

urlpatterns = [
    path("", views.feed, name="feed"),
    path("new/", views.post_create, name="post_create"),
    path("p/<slug:slug>/", views.post_detail, name="post_detail"),
    path("p/<slug:slug>/like/", views.like_toggle, name="like_toggle"),
    path("p/<slug:slug>/visibility/", views.visibility_toggle, name="visibility_toggle"),
    path("p/<slug:slug>/delete/", views.post_delete, name="post_delete"),
]
