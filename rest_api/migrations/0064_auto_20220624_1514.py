# Generated by Django 3.2.13 on 2022-06-24 19:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0063_alter_changeoprequest_related_routes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='changeopprocess',
            name='message',
        ),
        migrations.DeleteModel(
            name='ChangeOPProcessFile',
        ),
    ]