# Generated by Django 3.2.8 on 2021-10-21 23:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import rest_api.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Correo Electrónico')),
                ('access_to_ops', models.BooleanField(default=False, verbose_name='Acceso a Programas de Operación')),
                ('access_to_organizations', models.BooleanField(default=False, verbose_name='Acceso a Organizaciones')),
                ('access_to_users', models.BooleanField(default=False, verbose_name='Acceso a Usuarios')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', rest_api.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ChangeOPRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de Creación')),
                ('title', models.CharField(max_length=50, verbose_name='Titulo')),
                ('message', models.TextField(verbose_name='Mensaje')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de actualización')),
            ],
            options={
                'verbose_name': 'Solicitud de cambio de PO',
                'verbose_name_plural': 'Solicitudes de cambio de PO',
            },
        ),
        migrations.CreateModel(
            name='ChangeOPRequestMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de creación')),
                ('message', models.TextField(verbose_name='Mensaje')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='change_op_request_messages', to=settings.AUTH_USER_MODEL, verbose_name='Creador')),
            ],
            options={
                'verbose_name': 'Mensaje de solicitud de cambio de PO',
                'verbose_name_plural': 'Mensajes de solicitud de cambio de PO',
            },
        ),
        migrations.CreateModel(
            name='ChangeOPRequestStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Nombre')),
            ],
            options={
                'verbose_name': 'Estado de solicitud de cambio PO',
                'verbose_name_plural': 'Estados de solicitud de cambio PO',
            },
        ),
        migrations.CreateModel(
            name='ContractType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=7, verbose_name='Nombre')),
            ],
            options={
                'verbose_name': 'Tipo de Contrato',
                'verbose_name_plural': 'Tipos de Contrato',
            },
        ),
        migrations.CreateModel(
            name='OperationProgramType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, verbose_name='Nombre')),
            ],
            options={
                'verbose_name': 'Tipo de Programa de Operación',
                'verbose_name_plural': 'Tipos de Programa de Operación',
            },
        ),
        migrations.CreateModel(
            name='StatusLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de creación')),
                ('change_op_request', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='rest_api.changeoprequest', verbose_name='Solicitud de cambio de Programa de Operación')),
                ('new_status', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='rest_api.changeoprequeststatus', verbose_name='Estado nuevo')),
                ('previous_status', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='rest_api.changeoprequeststatus', verbose_name='Estado previo')),
            ],
            options={
                'verbose_name': 'Log de estado',
                'verbose_name_plural': 'Logs de estado',
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Nombre')),
                ('created_at', models.DateTimeField(verbose_name='Fecha de creación')),
                ('contract_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='organizations', to='rest_api.contracttype', verbose_name='Tipo de Contrato')),
                ('default_counterpart', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='organizations', to='rest_api.organization', verbose_name='Contraparte por defecto')),
                ('default_user_contact', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='organizations', to=settings.AUTH_USER_MODEL, verbose_name='Usuario de contacto por defecto')),
            ],
            options={
                'verbose_name': 'Organización',
                'verbose_name_plural': 'Organizaciones',
            },
        ),
        migrations.CreateModel(
            name='OperationProgramStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Nombre')),
                ('time_threshold', models.IntegerField(verbose_name='Días máximos antes de nuevo PO')),
                ('contract_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='operation_program_statuses', to='rest_api.contracttype', verbose_name='Tipo de Contrato')),
            ],
            options={
                'verbose_name': 'Estado de Programa de Operación',
                'verbose_name_plural': 'Estados de Programa de Operación',
            },
        ),
        migrations.CreateModel(
            name='OperationProgram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_at', models.DateField(unique=True, verbose_name='Fecha de inicio')),
                ('op_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ops', to='rest_api.operationprogramtype', verbose_name='Tipo de Programa de Operación')),
            ],
            options={
                'verbose_name': 'Programa de Operación',
                'verbose_name_plural': 'Programas de Operación',
            },
        ),
        migrations.CreateModel(
            name='OPChangeLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateField(default=django.utils.timezone.now, verbose_name='Fecha de creación')),
                ('change_op_request', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='op_change_logs', to='rest_api.changeoprequest', verbose_name='Programa de Operación')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='op_change_logs', to=settings.AUTH_USER_MODEL, verbose_name='Creador')),
                ('new_op', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='rest_api.operationprogram', verbose_name='Nuevo Programa de Operación')),
                ('previous_op', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='rest_api.operationprogram', verbose_name='Programa de Operación previo')),
            ],
            options={
                'verbose_name': 'Log de solicitud de cambio de PO',
                'verbose_name_plural': 'Logs de solicitud de cambio de PO',
            },
        ),
        migrations.AddField(
            model_name='changeoprequeststatus',
            name='contract_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='change_op_request_statuses', to='rest_api.contracttype', verbose_name='Tipo de Contrato'),
        ),
        migrations.CreateModel(
            name='ChangeOPRequestMessageFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='', verbose_name='Archivo')),
                ('change_op_request_message', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='change_op_request_message_files', to='rest_api.changeoprequestmessage', verbose_name='Mensaje de solicitud de cambio de Programa de Operación')),
            ],
            options={
                'verbose_name': 'Archivo asociado al mensaje de solicitud de cambio de PO',
                'verbose_name_plural': 'Archivos asociados a mensaje de solicitud de cambio de PO',
            },
        ),
        migrations.CreateModel(
            name='ChangeOPRequestFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='', verbose_name='Archivo')),
                ('change_op_request', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='change_op_request_files', to='rest_api.changeoprequest', verbose_name='Solicitud de cambio de Programa de Operación')),
            ],
            options={
                'verbose_name': 'Archivo de solicitud de cambio de PO',
                'verbose_name_plural': 'Archivos de solicitud de cambio de PO',
            },
        ),
        migrations.AddField(
            model_name='changeoprequest',
            name='contract_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='change_op_request', to='rest_api.contracttype', verbose_name='Tipo de Contrato'),
        ),
        migrations.AddField(
            model_name='changeoprequest',
            name='counterpart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='change_op_request', to='rest_api.organization', verbose_name='Contraparte'),
        ),
        migrations.AddField(
            model_name='changeoprequest',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='change_op_requests', to=settings.AUTH_USER_MODEL, verbose_name='Creador'),
        ),
        migrations.AddField(
            model_name='changeoprequest',
            name='op',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='change_op_requests', to='rest_api.operationprogram', verbose_name='Programa de Operación'),
        ),
        migrations.AddField(
            model_name='changeoprequest',
            name='status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='change_op_requests', to='rest_api.changeoprequeststatus', verbose_name='Estado'),
        ),
        migrations.AddField(
            model_name='user',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='rest_api.organization', verbose_name='Organización'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
