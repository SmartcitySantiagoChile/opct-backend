# Generated by Django 3.2.14 on 2022-08-29 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0082_alter_routedictionary_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changeopprocess',
            name='title',
            field=models.CharField(max_length=70, verbose_name='Titulo'),
        ),
    ]
