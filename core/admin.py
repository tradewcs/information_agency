from django.contrib import admin

from .models import Topik, NewsPaper


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
