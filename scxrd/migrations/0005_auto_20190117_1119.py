# Generated by Django 2.1.5 on 2019-01-17 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scxrd', '0004_auto_20190117_1029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='result_date',
            field=models.DateField(blank=True, null=True, verbose_name='results sent date'),
        ),
    ]