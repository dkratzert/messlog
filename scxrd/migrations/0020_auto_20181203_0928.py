# Generated by Django 2.1.3 on 2018-12-03 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scxrd', '0019_auto_20181203_0927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='machine',
            field=models.IntegerField(choices=[(1, 'APEX'), (2, 'Spider'), (3, 'VENTURE')], verbose_name='diffractometer'),
        ),
    ]
