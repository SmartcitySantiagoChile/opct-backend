# Generated by Django 3.2.8 on 2022-04-14 17:41

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0030_auto_20220413_1912'),
    ]

    operations = [
        migrations.AddField(
            model_name='changeopprocess',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de creación'),
        ),
    ]
