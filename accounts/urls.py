from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("edit/", views.profile_edit, name="profile_edit"),
    path("delete/", views.account_delete, name="account_delete"),
    path("<str:username>/", views.profile, name="profile"),
]
