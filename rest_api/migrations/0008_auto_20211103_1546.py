# Generated by Django 3.2.8 on 2021-11-03 15:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("rest_api", "0007_remove_organization_default_user_contact"),
    ]

    operations = [
        migrations.CreateModel(
            name="OPChangeDataLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("previous_data", models.JSONField(verbose_name="Datos anteriores")),
                ("new_data", models.JSONField(verbose_name="Datos nuevos")),
                (
                    "op",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="op_change_data_logs",
                        to="rest_api.operationprogram",
                        verbose_name="Programa de Operación",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="op_change_data_logs",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Usuario",
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(
            name="OPChangeDateLog",
        ),
    ]
