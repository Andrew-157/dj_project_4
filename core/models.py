from typing import Iterable, Optional
import uuid
from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator
from django.template.defaultfilters import slugify

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


class Tag(models.Model):
    name = models.CharField(max_length=255,
                            unique=True,
                            validators=[MinLengthValidator(2)])


class Article(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,
        editable=False
    )
    title = models.CharField(max_length=255,
                             validators=[MinLengthValidator(5)],
                             null=False)
    author = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    category = models.ForeignKey(
        'core.Category', on_delete=models.PROTECT, related_name='articles')
    published = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    is_ready = models.BooleanField(default=False)
    tags = models.ManyToManyField('core.Tag')

    def __str__(self):
        return str(self.id) + ' ' + self.title


class Section(models.Model):
    title = models.CharField(max_length=255,
                             validators=[MinLengthValidator(5)],
                             null=False)
    number = models.SmallIntegerField(
        validators=[MinValueValidator(1)], default=1, null=False)
    content = models.TextField()
    slug = models.CharField(max_length=300,
                            null=False)
    article = models.ForeignKey(
        'core.Article', on_delete=models.CASCADE, related_name='sections')

    published = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Section, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        unique_together = (
            ('article', 'number'),
            ('article', 'title')
        )
