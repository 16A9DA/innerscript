from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("edit/", views.profile_edit, name="profile_edit"),
    path("delete/", views.account_delete, name="account_delete"),
    path("<str:username>/delete/", views.admin_user_delete, name="admin_user_delete"),
    path("<str:username>/", views.profile, name="profile"),
]
