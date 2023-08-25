import uuid
from django.db import models
from django.core.validators import MinLengthValidator


class Category(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,
        editable=False)
    title = models.CharField(max_length=255,
                             validators=[MinLengthValidator(3)],
                             null=False, unique=True)
