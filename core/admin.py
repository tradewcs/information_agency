from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from .models import Publisher, Topik, NewsPaper


@admin.register(Publisher)
class PublisherAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "years_of_experience",
    )


@admin.register(Topik)
class TopikAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )


@admin.register(NewsPaper)
class NewsPaperAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "published_date",
    )
