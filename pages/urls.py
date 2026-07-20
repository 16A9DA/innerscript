from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("initiatives/", views.initiatives, name="initiatives"),
    path("toolkits/", views.toolkits, name="toolkits"),
    path("toolkits/upload/", views.toolkit_upload, name="toolkit_upload"),
    path("toolkits/<int:pk>/approve/", views.toolkit_approve, name="toolkit_approve"),
    path("impact/", views.impact, name="impact"),
    path("about/", views.about, name="about"),
    path("privacy/", views.privacy, name="privacy"),
]
