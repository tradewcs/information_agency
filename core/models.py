import uuid
from django.db import models
from django.conf import settings
from django.urls import reverse


# NOTE: `Publisher` model was moved to the `accounts` app. Refer to the
# user model via `settings.AUTH_USER_MODEL` to avoid hard imports here.


class Topik(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name


class ArticleInvite(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_invites",
    )
    newspaper = models.ForeignKey(
        "NewsPaper",
        on_delete=models.CASCADE,
        related_name="article_invites",
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    email = models.EmailField(blank=True, null=True)
    used = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return (
            f"ArticleInvite {self.token} for {self.newspaper.title} "
            f"by {self.created_by.username} -> {self.email or 'any'}"
        )


class NewsPaper(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    topic = models.ManyToManyField(
        Topik,
        related_name="newspapers"
    )
    publishers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="newspapers"
    )

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("core:newspaper_detail", args=[self.pk])
