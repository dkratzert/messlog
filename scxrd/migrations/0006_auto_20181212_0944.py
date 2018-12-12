# Generated by Django 2.1.4 on 2018-12-12 08:44

from django.db import migrations
import django.db.models.deletion
import filer.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0010_auto_20180414_2058'),
        ('scxrd', '0005_auto_20181211_1420'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='upload',
            name='upload',
        ),
        migrations.AddField(
            model_name='upload',
            name='cif',
            field=filer.fields.file.FilerFileField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cif_files', to='filer.File'),
        ),
    ]
