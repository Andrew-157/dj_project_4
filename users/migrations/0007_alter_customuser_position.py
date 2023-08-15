# Generated by Django 4.2.4 on 2023-08-15 15:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_customuser_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='position',
            field=models.CharField(blank=True, max_length=255, null=True, validators=[django.core.validators.MinLengthValidator(3)]),
        ),
    ]
