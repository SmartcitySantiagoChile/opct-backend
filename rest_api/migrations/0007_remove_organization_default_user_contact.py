# Generated by Django 3.2.8 on 2021-11-03 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rest_api", "0006_auto_20211103_1332"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="organization",
            name="default_user_contact",
        ),
    ]
