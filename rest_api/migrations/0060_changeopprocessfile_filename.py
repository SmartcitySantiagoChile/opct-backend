# Generated by Django 3.2.13 on 2022-06-22 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0059_alter_changeoprequestlog_change_op_request'),
    ]

    operations = [
        migrations.AddField(
            model_name='changeopprocessfile',
            name='filename',
            field=models.CharField(default='filename', max_length=128),
            preserve_default=False,
        ),
    ]