# Generated by Django 2.1.5 on 2019-01-16 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scxrd', '0002_auto_20190116_1401'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='experiment',
            field=models.CharField(default='', max_length=200, unique=True, verbose_name='experiment name'),
        ),
    ]
