import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class Publisher(AbstractUser):
    password = models.CharField(max_length=128)
    years_of_experience = models.PositiveIntegerField(default=0)
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Topik(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name="email_tokens",
    )
    token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.username}: {self.token}"


class ArticleInvite(models.Model):
    created_by = models.ForeignKey(
        Publisher,
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

    def __str__(self):
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
        Publisher,
        related_name="newspapers"
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:newspaper_detail", args=[self.pk])
