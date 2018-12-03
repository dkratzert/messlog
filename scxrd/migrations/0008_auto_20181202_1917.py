# Generated by Django 2.1.3 on 2018-12-02 18:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scxrd', '0007_auto_20181202_1906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='number',
            field=models.IntegerField(unique=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='number'),
        ),
    ]