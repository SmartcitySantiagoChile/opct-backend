# Generated by Django 3.2.8 on 2021-10-18 21:23

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SendMailJobExecution",
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
                (
                    "jobId",
                    models.UUIDField(
                        null=True, verbose_name="Identificador de trabajo"
                    ),
                ),
                ("enqueueTimestamp", models.DateTimeField(verbose_name="Encolado")),
                (
                    "executionStart",
                    models.DateTimeField(null=True, verbose_name="Inicio"),
                ),
                ("executionEnd", models.DateTimeField(null=True, verbose_name="Fin")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("enqueued", "Encolado"),
                            ("running", "Cargando datos"),
                            ("finished", "Finalización exitosa"),
                            ("failed", "Finalización con error"),
                            ("canceled", "Cancelado por usuario"),
                            ("expired", "Vencido"),
                        ],
                        max_length=10,
                        verbose_name="Estado",
                    ),
                ),
                (
                    "errorMessage",
                    models.TextField(
                        default="", max_length=500, verbose_name="Mensaje de error"
                    ),
                ),
                ("subject", models.TextField(verbose_name="Asunto")),
                ("body", models.TextField(verbose_name="Cuerpo del mensaje")),
                (
                    "users",
                    models.ManyToManyField(
                        to=settings.AUTH_USER_MODEL, verbose_name="Lista de Usuarios"
                    ),
                ),
            ],
            options={
                "verbose_name": "Trabajo para enviar correo",
                "verbose_name_plural": "Trabajos para enviar correos",
            },
        ),
    ]
