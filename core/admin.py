from django.contrib import admin

from .models import User, Recipe, Tag

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name']
    ordering = ['id']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'price', 'link']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'user']
