from django.core.validators import MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser


class Publisher(AbstractUser):
    years_of_experience = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(80)],
    )

    def __str__(self) -> str:
        return self.username
