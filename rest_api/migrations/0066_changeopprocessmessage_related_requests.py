# Generated by Django 3.2.13 on 2022-07-14 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0065_alter_changeopprocesslog_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='changeopprocessmessage',
            name='related_requests',
            field=models.ManyToManyField(to='rest_api.ChangeOPRequest'),
        ),
    ]