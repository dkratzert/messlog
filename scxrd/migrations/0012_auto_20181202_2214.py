# Generated by Django 2.1.3 on 2018-12-02 21:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('scxrd', '0011_auto_20181202_2144'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='experiment',
            name='date',
        ),
        migrations.AddField(
            model_name='experiment',
            name='measure_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='measurement date'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='result_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='structure results date'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='submit_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='sample submission date'),
        ),
    ]
