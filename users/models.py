from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser

def validate_image(image):
    file_size = image.file.size

    limit_mb = 5
    if file_size > limit_mb * 1024**2:
        raise ValidationError(f"Maximum size of profile image is {limit_mb} MB")


help_text_for_position = 'Optional: State your position. For example: teacher, student, scientist, etc..'


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    position = models.CharField(null=True, help_text=help_text_for_position, max_length=255)
    image = models.ImageField(null=True, blank=True,
                              upload_to='users/images', validators=[validate_image])