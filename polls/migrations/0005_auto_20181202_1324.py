# Generated by Django 2.1.3 on 2018-12-02 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0004_auto_20181202_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='measurement',
            name='used_machine',
            field=models.IntegerField(choices=[(1, 'x.name'), (2, 'x.name')]),
        ),
    ]
