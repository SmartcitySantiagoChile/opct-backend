# Generated by Django 3.2.8 on 2021-10-25 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changeoprequeststatus',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Nombre'),
        ),
    ]
