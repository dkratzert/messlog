# Generated by Django 2.1.5 on 2019-01-14 16:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scxrd', '0003_auto_20190114_1731'),
        ('myuser', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='work_group',
        ),
        migrations.RemoveField(
            model_name='workgroup',
            name='group_head',
        ),
        migrations.DeleteModel(
            name='Person',
        ),
        migrations.DeleteModel(
            name='WorkGroup',
        ),
    ]
