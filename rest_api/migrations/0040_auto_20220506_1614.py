# Generated by Django 3.2.8 on 2022-05-06 20:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("rest_api", "0039_auto_20220501_1649"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="changeopprocess",
            name="change_op_requests",
        ),
        migrations.RemoveField(
            model_name="changeoprequest",
            name="op_release_date",
        ),
        migrations.AddField(
            model_name="changeoprequest",
            name="change_op_process",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="change_op_requests",
                to="rest_api.changeopprocess",
                verbose_name="Solicitudes de cambio",
            ),
            preserve_default=False,
        ),
    ]
