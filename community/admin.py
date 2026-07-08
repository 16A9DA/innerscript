from django.contrib import admin

from .models import Category, Comment, Like, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "kind", "category", "created")
    list_filter = ("kind", "category")
    search_fields = ("title", "body")


admin.site.register(Comment)
admin.site.register(Like)
