import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.core.validators import MaxValueValidator


class Publisher(AbstractUser):
    password = models.CharField(max_length=128)
    years_of_experience = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(80)],
    )

    def __str__(self) -> str:
        return self.username


class Topik(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name


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
        Publisher,
        related_name="newspapers"
    )

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("core:newspaper_detail", args=[self.pk])
