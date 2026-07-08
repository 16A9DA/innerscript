from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("initiatives/", views.initiatives, name="initiatives"),
    path("toolkits/", views.toolkits, name="toolkits"),
    path("impact/", views.impact, name="impact"),
    path("about/", views.about, name="about"),
    path("privacy/", views.privacy, name="privacy"),
]
