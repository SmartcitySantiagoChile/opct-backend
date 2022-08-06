from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.models import Group
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, organization, access_to_ops, access_to_organizations, access_to_users,
                     access_to_upload_route_dictionary,
                     **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            organization=organization,
            access_to_ops=access_to_ops,
            access_to_organizations=access_to_organizations,
            access_to_users=access_to_users,
            access_to_upload_route_dictionary=access_to_upload_route_dictionary,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        if access_to_ops:
            user.groups.add(Group.objects.get(name="Operation Program"))
        if access_to_organizations:
            user.groups.add(Group.objects.get(name="Organization"))
        if access_to_users:
            user.groups.add(Group.objects.get(name="User"))
        if access_to_upload_route_dictionary:
            user.groups.add(Group.objects.get(name="Upload Route Dictionary"))
        user.save()
        return user

    def create_user(self, email, password, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("organization", None)
        extra_fields.setdefault("access_to_ops", True)
        extra_fields.setdefault("access_to_organizations", True)
        extra_fields.setdefault("access_to_users", True)
        extra_fields.setdefault("access_to_upload_route_dictionary", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class ContractType(models.Model):
    name = models.CharField("Nombre", max_length=7)
    OLD = 1
    NEW = 2
    BOTH = 3

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Tipo de Contrato"
        verbose_name_plural = "Tipos de Contrato"


class OperationProgramType(models.Model):
    name = models.CharField("Nombre", max_length=10)
    BASE = 1
    MODIFIED = 2
    SPECIAL = 3

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Tipo de Programa de Operación"
        verbose_name_plural = "Tipos de Programa de Operación"


class OperationProgramStatus(models.Model):
    name = models.CharField("Nombre", max_length=50)
    time_threshold = models.IntegerField("Días máximos antes de nuevo PO")
    contract_type = models.ForeignKey(
        ContractType,
        related_name="operation_program_statuses",
        blank=False,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Contrato",
    )

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Estado de Programa de Operación"
        verbose_name_plural = "Estados de Programa de Operación"


class OperationProgram(models.Model):
    start_at = models.DateField("Fecha de implementación", unique=True)
    op_type = models.ForeignKey(OperationProgramType, related_name="ops", on_delete=models.PROTECT,
                                verbose_name="Tipo de Programa de Operación")

    def __str__(self):
        return '{0} ({1})'.format(self.start_at, self.op_type.name)

    class Meta:
        verbose_name = "Programa de Operación"
        verbose_name_plural = "Programas de Operación"


class CounterPartContact(models.Model):
    organization = models.ForeignKey("Organization", related_name="counter_part_contacts", on_delete=models.PROTECT,
                                     verbose_name="Organización")
    counter_part_user = models.ForeignKey("User", related_name="counter_part_contact", on_delete=models.PROTECT,
                                          verbose_name="Contacto de contraparte")

    def save(self, *args, **kwargs):
        user_organization = self.counter_part_user.organization_id
        if user_organization != self.organization.pk:
            super(CounterPartContact, self).save(*args, **kwargs)
        else:
            raise ValueError("El usuario debe pertenecer a una organización distinta")

    def __str__(self):
        return str(self.counter_part_user)

    class Meta:
        verbose_name = "Contacto de contraparte"
        verbose_name_plural = "Contactos de contraparte"


class Organization(models.Model):
    name = models.CharField("Nombre", max_length=50)
    created_at = models.DateTimeField("Fecha de creación")
    contract_type = models.ForeignKey(ContractType, related_name="organizations", blank=False, on_delete=models.PROTECT,
                                      verbose_name="Tipo de Contrato")
    default_counterpart = models.ForeignKey("self", related_name="organizations", blank=True, on_delete=models.PROTECT,
                                            verbose_name="Organización que será contraparte por defecto", null=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"


class User(AbstractUser):
    """User model."""
    username = None
    email = models.EmailField(_("Correo Electrónico"), unique=True)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, null=True, verbose_name="Organización",
                                     blank=True)
    access_to_ops = models.BooleanField("Acceso a Programas de Operación", default=False)
    access_to_organizations = models.BooleanField("Acceso a Organizaciones", default=False)
    access_to_users = models.BooleanField("Acceso a Usuarios", default=False)
    access_to_upload_route_dictionary = models.BooleanField("Acceso a subir diccionario de servicios", default=False)

    CONTRACT_ADMINISTRATOR = "contract_administrator"
    PLANNING_TECHNICIAN = "planning_technician"
    PROSECUTOR = "prosecutor"

    ROLE_CHOICES = [
        (CONTRACT_ADMINISTRATOR, "Administrador de contrato"),
        (PLANNING_TECHNICIAN, "Técnico de planificación"),
        (PROSECUTOR, "Fiscal"),
    ]

    role = models.CharField("Rol", max_length=30, choices=ROLE_CHOICES)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


class ChangeOPProcess(models.Model):
    title = models.CharField("Titulo", max_length=50)
    created_at = models.DateTimeField("Fecha de creación", default=timezone.now)
    updated_at = models.DateTimeField("Fecha de la última actualización", default=timezone.now)
    counterpart = models.ForeignKey(Organization, related_name="change_op_processes", on_delete=models.PROTECT,
                                    verbose_name="Contraparte")
    contract_type = models.ForeignKey(ContractType, related_name="change_op_processes", on_delete=models.PROTECT,
                                      verbose_name="Tipo de Contrato")
    operation_program = models.ForeignKey(OperationProgram, related_name="change_op_processes",
                                          on_delete=models.PROTECT, verbose_name="Programa de Operación",
                                          blank=True, null=True)
    creator = models.ForeignKey(User, related_name="change_op_processes", on_delete=models.PROTECT, blank=False,
                                verbose_name="Usuario creador del proceso")
    status = models.ForeignKey('ChangeOPProcessStatus', related_name="+", on_delete=models.PROTECT,
                               verbose_name="Estado")
    op_release_date = models.DateField("Fecha de implementación", blank=True, null=True)

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = "Proceso de cambio de PO"
        verbose_name_plural = "Procesos de cambio de PO"


class ChangeOPProcessStatus(models.Model):
    """
    Listado de estados que puede tener un proceso de cambio de PO según el tipo de contrato asociado al proceso
    """
    name = models.CharField("Nombre", max_length=100)
    contract_type = models.ForeignKey(ContractType, related_name="change_op_process_statuses", on_delete=models.PROTECT,
                                      verbose_name="Tipo de Contrato", blank=False)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Estado de proceso de cambio PO"
        verbose_name_plural = "Estados de proceso de cambio PO"


class ChangeOPRequest(models.Model):
    title = models.CharField("Titulo", max_length=50)
    created_at = models.DateTimeField("Fecha de Creación", default=timezone.now)
    creator = models.ForeignKey(User, related_name="change_op_requests", on_delete=models.PROTECT, blank=False,
                                verbose_name="Usuario creador del proceso")
    operation_program = models.ForeignKey(OperationProgram, related_name="change_op_requests", on_delete=models.PROTECT,
                                          verbose_name="Programa de Operación", blank=True, null=True)
    status = models.ForeignKey('ChangeOPRequestStatus', related_name="change_op_requests", on_delete=models.PROTECT,
                               verbose_name="Estado")
    updated_at = models.DateTimeField("Fecha de actualización", default=timezone.now)
    SHORTENING = "shortening"
    PARAMETERS_ADJUSTMENT = "parameters_adjustment"
    CAPACITY_ADJUSTMENT = "capacity_adjustment"
    FREQUENCY_ADJUSTMENT = "frequency_adjustment"
    OPERATIONAL_ADJUSTMENT = "operational_adjustment"
    STOP_CHANGE = "stop_change"
    SPEED_CHANGE = "speed_change"
    OPERATION_SCHEDULE_CHANGE = "operation_schedule_change"
    ROUND_UP_SERVICE = "round_up_service"
    DELETE = "delete"
    EXTENSION = "extension"
    TERMINAL_EXTENSION = "terminal_extension"
    FAIR_AND_OR_BIKE_WAY = "fair_and_or_bike_way"
    FUSION = "fusion"
    INTEGRATED_KM = "integrated_km"
    PATH_MODIFICATION = "path_modification"
    HEAD_MODIFICATION = "head_modification"
    NEW_SERVICE = "new_service"
    BUS_TYPOLOGY = "bus_typology"
    OTHER = "other"
    REASON_CHOICES = [
        (SHORTENING, "Acortamiento"),
        (PARAMETERS_ADJUSTMENT, "Ajuste de Parámetros"),
        (CAPACITY_ADJUSTMENT, "Ajuste de Capacidades"),
        (FREQUENCY_ADJUSTMENT, "Ajuste de Frecuencias"),
        (OPERATIONAL_ADJUSTMENT, "Ajuste Operacional"),
        (STOP_CHANGE, "Cambios de Paradas"),
        (SPEED_CHANGE, "Cambios de Velocidades"),
        (OPERATION_SCHEDULE_CHANGE, "Cambios Horarios de Operación"),
        (ROUND_UP_SERVICE, "Circunvalar Servicio"),
        (DELETE, "Eliminación"),
        (TERMINAL_EXTENSION, "Extensión a Terminal"),
        (FAIR_AND_OR_BIKE_WAY, "Feria y/o Ciclorecreovía"),
        (FUSION, "Fusión"),
        (INTEGRATED_KM, "Km Integrados"),
        (PATH_MODIFICATION, "Modificación de Trazado"),
        (HEAD_MODIFICATION, "Modificación de Cabezal"),
        (NEW_SERVICE, "Nuevo Servicio"),
        (BUS_TYPOLOGY, "Tipología de Bus"),
        (OTHER, "Otros"),
    ]
    reason = models.CharField("Motivo", max_length=30, choices=REASON_CHOICES)
    related_requests = models.ManyToManyField("self", blank=True, verbose_name="Solicitudes relacionadas")
    change_op_process = models.ForeignKey("ChangeOPProcess", related_name="change_op_requests",
                                          on_delete=models.PROTECT, null=False, blank=False,
                                          verbose_name="Proceso de cambio de PO")
    related_routes = ArrayField(models.CharField(max_length=30, blank=True))

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = "Solicitud de modificación de PO"
        verbose_name_plural = "Solicitudes de modificación de PO"


class ChangeOPRequestStatus(models.Model):
    """
    Listado de estados que puede tener una solicitud de modificación según el tipo de contrato asociado al proceso
    """
    name = models.CharField("Nombre", max_length=100)
    contract_type = models.ForeignKey(ContractType, related_name="change_op_request_statuses", blank=False,
                                      on_delete=models.PROTECT, verbose_name="Tipo de Contrato")

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Estado de solicitud de cambio PO"
        verbose_name_plural = "Estados de solicitud de cambio PO"


class ChangeOPRequestLog(models.Model):
    """
    Historial de modificaciones a una solicitud de modificación
    """
    created_at = models.DateTimeField("Fecha de creación", default=timezone.now)
    CHANGE_OP_REQUEST_CREATION = 'change_op_request_creation'
    CHANGE_OP_REQUEST_UPDATE = 'change_op_request_update'
    TYPE_CHOICES = (
        (CHANGE_OP_REQUEST_UPDATE, 'Actualización de datos'),
        (CHANGE_OP_REQUEST_CREATION, 'Creación de solicitud'),
    )
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, null=False)
    user = models.ForeignKey(User, related_name="+", on_delete=models.PROTECT,
                             verbose_name="Usuario que realizó la acción")
    previous_data = models.JSONField("Datos anteriores")
    new_data = models.JSONField("Datos nuevos")
    change_op_request = models.ForeignKey(ChangeOPRequest, related_name="change_op_requests_logs",
                                          on_delete=models.PROTECT, verbose_name="Solicitud de modificación")

    def __str__(self):
        return '{0} -> {1}: {2}'.format(self.change_op_request, self.created_at, self.type)

    class Meta:
        verbose_name = "Log de estado"
        verbose_name_plural = "Logs de estado"


class OPChangeLog(models.Model):
    """
    Historial de modificaciones a un programa de operación
    """
    created_at = models.DateTimeField("Fecha de creación", default=timezone.now)
    user = models.ForeignKey(User, related_name="op_change_data_logs", on_delete=models.PROTECT, verbose_name="Usuario")
    previous_data = models.JSONField("Datos anteriores")
    new_data = models.JSONField("Datos nuevos")
    operation_program = models.ForeignKey(OperationProgram, related_name="op_change_logs",
                                          on_delete=models.PROTECT, verbose_name="Programa de Operación")

    def __str__(self):
        return str(self.created_at)

    class Meta:
        verbose_name = "Log de cambios de PO"
        verbose_name_plural = "Logs de cambios de PO"


class ChangeOPProcessLog(models.Model):
    """
    Historial de modificaciones a un proceso de cambio de programa de operación
    """
    created_at = models.DateTimeField("Fecha de creación", default=timezone.now)
    STATUS_CHANGE = 'status_change'
    OP_CHANGE = 'op_change'
    OP_CHANGE_WITH_DEADLINE_UPDATED = 'op_change_with_deadline_updated'
    TYPE_CHOICES = (
        (STATUS_CHANGE, 'Cambio de estado'),
        (OP_CHANGE, 'Cambio de programa de operación'),
        (OP_CHANGE_WITH_DEADLINE_UPDATED, 'Cambio de programa de operación con actualización de deadlines'),
    )
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, null=False)
    user = models.ForeignKey(User, related_name="+", on_delete=models.PROTECT, verbose_name="Usuario")
    previous_data = models.JSONField("Datos anteriores")
    new_data = models.JSONField("Datos nuevos")
    change_op_process = models.ForeignKey(ChangeOPProcess, related_name="change_op_process_logs",
                                          on_delete=models.PROTECT, verbose_name="Proceso de cambio de PO")

    def __str__(self):
        return '{0} -> {1}: {2}'.format(self.change_op_process, self.created_at, self.type)

    class Meta:
        verbose_name = "Log de estado de proceso"
        verbose_name_plural = "Logs de estado de proceso"


class ChangeOPProcessMessage(models.Model):
    created_at = models.DateTimeField("Fecha de creación", default=timezone.now)
    creator = models.ForeignKey(User, related_name="change_op_process_messages", on_delete=models.PROTECT, blank=False,
                                null=False, verbose_name="Creador")
    message = models.TextField("Mensaje")
    change_op_process = models.ForeignKey(ChangeOPProcess, related_name="change_op_process_messages",
                                          on_delete=models.PROTECT, null=False, verbose_name="¨Proceso de cambio de PO")
    related_requests = models.ManyToManyField(ChangeOPRequest)

    def __str__(self):
        return str(self.message)

    class Meta:
        verbose_name = "Mensaje de proceso de cambio de PO"
        verbose_name_plural = "Mensajes de proceso de cambio de PO"


def get_upload_to(instance, filename):
    return '{0}/{1}'.format(instance.change_op_process_message.change_op_process_id, filename)


class ChangeOPProcessMessageFile(models.Model):
    filename = models.CharField(max_length=128, null=False)
    size = models.IntegerField(null=False, help_text="The size, in bytes, of the uploaded file.")
    file = models.FileField("Archivo", upload_to=get_upload_to)
    change_op_process_message = models.ForeignKey(ChangeOPProcessMessage,
                                                  related_name="change_op_process_message_files",
                                                  on_delete=models.PROTECT,
                                                  verbose_name="Mensaje de proceso de cambio de PO")

    def __str__(self):
        return str(self.file)

    class Meta:
        verbose_name = "Archivo asociado a un mensaje de proceso de cambio de PO"
        verbose_name_plural = "Archivos asociados a mensajes de procesos de cambio de PO"


class RouteDictionary(models.Model):
    """ Operation program to know routes available """
    auth_route_code = models.CharField("Código transantiago", max_length=30, unique=True)
    op_route_code = models.CharField("Código de operación", max_length=30)
    user_route_code = models.CharField("Código de usuario", max_length=30, null=True)
    route_type = models.CharField("Tipo de ruta", max_length=30, null=True)
    created_at = models.DateTimeField("Fecha de creación", null=True)
    operator = models.CharField(max_length=30)

    class Meta:
        verbose_name = "diccionario PO "
        verbose_name_plural = "diccionarios PO"
