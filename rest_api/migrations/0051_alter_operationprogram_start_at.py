# Generated by Django 3.2.13 on 2022-06-16 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0050_alter_organization_default_counterpart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operationprogram',
            name='start_at',
            field=models.DateField(unique=True, verbose_name='Fecha de implementación'),
        ),
    ]
