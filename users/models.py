from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import AbstractUser


def validate_image(image):
    file_size = image.file.size

    limit_mb = 5
    if file_size > limit_mb * 1024**2:
        raise ValidationError(
            f"Maximum size of profile image is {limit_mb} MB")


class CustomUser(AbstractUser):
    email = models.EmailField(
        unique=True, help_text='Required. Enter valid email address.')
    position = models.CharField(null=True, max_length=255,
                                validators=[MinLengthValidator(3)], blank=True,
                                help_text='Optional. For example: Computer Science Student, Arts Teacher, Rocket Engineer.')
