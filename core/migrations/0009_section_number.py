# Generated by Django 4.2.4 on 2023-08-27 10:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_section'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='number',
            field=models.SmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
