# Generated by Django 3.2.13 on 2022-06-15 13:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0048_rename_user_counterpartcontact_counter_part_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='counterpartcontact',
            name='counter_part_organization',
        ),
    ]
