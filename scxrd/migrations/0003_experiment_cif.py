# Generated by Django 2.1.4 on 2018-12-09 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scxrd', '0002_auto_20181207_2132'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='cif',
            field=models.FileField(default='', upload_to='scxrd/cifs'),
            preserve_default=False,
        ),
    ]
