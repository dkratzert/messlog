# Generated by Django 2.1.5 on 2019-01-14 16:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scxrd', '0003_auto_20190114_1731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workgroup',
            name='group_head',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='group', to='scxrd.Person'),
        ),
    ]
