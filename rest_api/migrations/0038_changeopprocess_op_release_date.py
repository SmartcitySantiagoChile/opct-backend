# Generated by Django 3.2.8 on 2022-05-01 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rest_api", "0037_alter_changeopprocessstatuslog_change_op_process"),
    ]

    operations = [
        migrations.AddField(
            model_name="changeopprocess",
            name="op_release_date",
            field=models.DateField(
                blank=True, null=True, verbose_name="Fecha de implementación"
            ),
        ),
    ]
