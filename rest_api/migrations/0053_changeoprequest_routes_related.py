# Generated by Django 3.2.13 on 2022-06-18 06:32

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0052_auto_20220618_0135'),
    ]

    operations = [
        migrations.AddField(
            model_name='changeoprequest',
            name='routes_related',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=30), default=[], size=None),
            preserve_default=False,
        ),
    ]