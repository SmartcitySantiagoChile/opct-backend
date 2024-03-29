# Generated by Django 3.2.13 on 2022-06-18 05:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0051_alter_operationprogram_start_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeOPProcessLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de creación')),
                ('type', models.CharField(choices=[('status_change', 'Cambio de estado'), ('op_change', 'Cambio de programa de operación'), ('op_change_with_deadline_updated', 'Cambio de programa de operación con actualización de deadlines')], max_length=50)),
                ('previous_data', models.JSONField(verbose_name='Datos anteriores')),
                ('new_data', models.JSONField(verbose_name='Datos nuevos')),
            ],
            options={
                'verbose_name': 'Log de estado de proceso',
                'verbose_name_plural': 'Logs de estado de proceso',
            },
        ),
        migrations.CreateModel(
            name='ChangeOPRequestLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de creación')),
                ('type', models.CharField(choices=[('status_change', 'Cambio de estado'), ('op_change', 'Cambio de programa de operación'), ('op_change_with_deadline_updated', 'Cambio de programa de operación con actualización de deadlines'), ('reason_change', 'Se actualizó el motivo de modificación')], max_length=50)),
                ('previous_data', models.JSONField(verbose_name='Datos anteriores')),
                ('new_data', models.JSONField(verbose_name='Datos nuevos')),
            ],
            options={
                'verbose_name': 'Log de estado',
                'verbose_name_plural': 'Logs de estado',
            },
        ),
        migrations.RemoveField(
            model_name='changeoprequestopchangelog',
            name='change_op_request',
        ),
        migrations.RemoveField(
            model_name='changeoprequestopchangelog',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='changeoprequestopchangelog',
            name='new_op',
        ),
        migrations.RemoveField(
            model_name='changeoprequestopchangelog',
            name='previous_op',
        ),
        migrations.RemoveField(
            model_name='changeoprequestreasonchangelog',
            name='change_op_request',
        ),
        migrations.RemoveField(
            model_name='changeoprequestreasonchangelog',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='opchangedatalog',
            name='op',
        ),
        migrations.RemoveField(
            model_name='opchangedatalog',
            name='user',
        ),
        migrations.RemoveField(
            model_name='statuslog',
            name='change_op_request',
        ),
        migrations.RemoveField(
            model_name='statuslog',
            name='new_status',
        ),
        migrations.RemoveField(
            model_name='statuslog',
            name='previous_status',
        ),
        migrations.RemoveField(
            model_name='statuslog',
            name='user',
        ),
        migrations.AlterModelOptions(
            name='changeopprocessmessagefile',
            options={'verbose_name': 'Archivo asociado a un mensaje de proceso de cambio de PO', 'verbose_name_plural': 'Archivos asociados a mensajes de procesos de cambio de PO'},
        ),
        migrations.AlterModelOptions(
            name='changeoprequest',
            options={'verbose_name': 'Solicitud de modificación de PO', 'verbose_name_plural': 'Solicitudes de modificación de PO'},
        ),
        migrations.AlterModelOptions(
            name='opchangelog',
            options={'verbose_name': 'Log de cambios de PO', 'verbose_name_plural': 'Logs de cambios de PO'},
        ),
        migrations.RemoveField(
            model_name='changeopprocess',
            name='base_op',
        ),
        migrations.RemoveField(
            model_name='opchangelog',
            name='change_op_process',
        ),
        migrations.RemoveField(
            model_name='opchangelog',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='opchangelog',
            name='new_op',
        ),
        migrations.RemoveField(
            model_name='opchangelog',
            name='previous_op',
        ),
        migrations.RemoveField(
            model_name='opchangelog',
            name='update_deadlines',
        ),
        migrations.AddField(
            model_name='changeopprocess',
            name='operation_program',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='change_op_processes', to='rest_api.operationprogram', verbose_name='Programa de Operación'),
        ),
        migrations.AddField(
            model_name='opchangelog',
            name='new_data',
            field=models.JSONField(default='', verbose_name='Datos nuevos'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='opchangelog',
            name='operation_program',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, related_name='op_change_data_logs', to='rest_api.operationprogram', verbose_name='Programa de Operación'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='opchangelog',
            name='previous_data',
            field=models.JSONField(default=None, verbose_name='Datos anteriores'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='opchangelog',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, related_name='op_change_data_logs', to='rest_api.user', verbose_name='Usuario'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='changeopprocess',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='change_op_processes', to=settings.AUTH_USER_MODEL, verbose_name='Usuario creador del proceso'),
        ),
        migrations.AlterField(
            model_name='changeopprocess',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de la última actualización'),
        ),
        migrations.AlterField(
            model_name='changeopprocessfile',
            name='change_op_process',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='change_op_process_files', to='rest_api.changeopprocess', verbose_name='Proceso de cambio de PO'),
        ),
        migrations.AlterField(
            model_name='changeopprocessmessage',
            name='change_op_process',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='change_op_process_messages', to='rest_api.changeopprocess', verbose_name='¨Proceso de cambio de PO'),
        ),
        migrations.AlterField(
            model_name='changeopprocessmessagefile',
            name='change_op_process_message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='change_op_process_message_files', to='rest_api.changeopprocessmessage', verbose_name='Mensaje de proceso de cambio de PO'),
        ),
        migrations.DeleteModel(
            name='ChangeOPProcessStatusLog',
        ),
        migrations.DeleteModel(
            name='ChangeOPRequestOPChangeLog',
        ),
        migrations.DeleteModel(
            name='ChangeOPRequestReasonChangeLog',
        ),
        migrations.DeleteModel(
            name='OPChangeDataLog',
        ),
        migrations.DeleteModel(
            name='StatusLog',
        ),
        migrations.AddField(
            model_name='changeoprequestlog',
            name='change_op_request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='status_logs', to='rest_api.changeoprequest', verbose_name='Solicitud de modificación'),
        ),
        migrations.AddField(
            model_name='changeoprequestlog',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Usuario que realizó la acción'),
        ),
        migrations.AddField(
            model_name='changeopprocesslog',
            name='change_op_process',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='change_op_process_status_logs', to='rest_api.changeopprocess', verbose_name='Proceso de cambio de PO'),
        ),
        migrations.AddField(
            model_name='changeopprocesslog',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Usuario'),
        ),
    ]
