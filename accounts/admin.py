from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from .models import Publisher


@admin.register(Publisher)
class PublisherAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "years_of_experience",
    )
