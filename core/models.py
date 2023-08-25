import uuid
from django.db import models
from django.core.validators import MinLengthValidator

from users.models import CustomUser


class Category(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,
        editable=False)
    title = models.CharField(max_length=255,
                             validators=[MinLengthValidator(3)],
                             null=False, unique=True)

    def __str__(self):
        return self.title


class Article(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,
        editable=False
    )
    title = models.CharField(max_length=255,
                             validators=[MinLengthValidator(5)],
                             null=False)
    author = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    category = models.ForeignKey('core.Category', on_delete=models.CASCADE)

    def __str__(self):
        return self.id + ' ' + self.title
