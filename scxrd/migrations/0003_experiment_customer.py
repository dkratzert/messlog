# Generated by Django 2.1.4 on 2018-12-10 15:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scxrd', '0002_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='scxrd.Customer'),
        ),
    ]