from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.models import Group
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(
        self,
        email,
        password,
        organization,
        access_to_ops,
        access_to_organizations,
        access_to_users,
        **extra_fields
    ):
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
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class ContractType(models.Model):
    name = models.CharField("Nombre", max_length=7)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Tipo de Contrato"
        verbose_name_plural = "Tipos de Contrato"


class OperationProgramType(models.Model):
    name = models.CharField("Nombre", max_length=10)

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
    start_at = models.DateField("Fecha de inicio", unique=True)
    op_type = models.ForeignKey(
        OperationProgramType,
        related_name="ops",
        on_delete=models.PROTECT,
        verbose_name="Tipo de Programa de Operación",
    )

    def __str__(self):
        return str(self.start_at)

    class Meta:
        verbose_name = "Programa de Operación"
        verbose_name_plural = "Programas de Operación"


class CounterPartContact(models.Model):
    user = models.ForeignKey(
        "User",
        related_name="counter_part_contacts",
        on_delete=models.PROTECT,
        verbose_name="Contacto de contraparte",
    )
    organization = models.ForeignKey(
        "Organization",
        related_name="counter_part_contacts",
        on_delete=models.PROTECT,
        verbose_name="Organización",
    )


class Organization(models.Model):
    name = models.CharField("Nombre", max_length=50)
    created_at = models.DateTimeField("Fecha de creación")
    contract_type = models.ForeignKey(
        ContractType,
        related_name="organizations",
        blank=False,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Contrato",
    )
    default_counterpart = models.ForeignKey(
        "self",
        related_name="organizations",
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="Contraparte por defecto",
        null=True,
    )
    default_user_contact = models.ForeignKey(
        "User",
        blank=True,
        related_name="organizations",
        on_delete=models.PROTECT,
        verbose_name="Usuario de contacto por defecto",
    )

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"


class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_("Correo Electrónico"), unique=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        null=True,
        verbose_name="Organización",
        blank=True,
    )
    access_to_ops = models.BooleanField(
        "Acceso a Programas de Operación", default=False
    )
    access_to_organizations = models.BooleanField(
        "Acceso a Organizaciones", default=False
    )
    access_to_users = models.BooleanField("Acceso a Usuarios", default=False)

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


class ChangeOPRequestStatus(models.Model):
    name = models.CharField("Nombre", max_length=100)
    contract_type = models.ForeignKey(
        ContractType,
        related_name="change_op_request_statuses",
        blank=False,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Contrato",
    )

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Estado de solicitud de cambio PO"
        verbose_name_plural = "Estados de solicitud de cambio PO"


class ChangeOPRequest(models.Model):
    created_at = models.DateTimeField("Fecha de Creación", default=timezone.now)
    creator = models.ForeignKey(
        User,
        related_name="change_op_requests",
        on_delete=models.PROTECT,
        blank=False,
        verbose_name="Creador",
    )
    op = models.ForeignKey(
        OperationProgram,
        related_name="change_op_requests",
        on_delete=models.PROTECT,
        verbose_name="Programa de Operación",
    )
    status = models.ForeignKey(
        ChangeOPRequestStatus,
        related_name="change_op_requests",
        on_delete=models.PROTECT,
        verbose_name="Estado",
    )
    counterpart = models.ForeignKey(
        Organization,
        related_name="change_op_request",
        on_delete=models.PROTECT,
        verbose_name="Contraparte",
    )
    contract_type = models.ForeignKey(
        ContractType,
        related_name="change_op_request",
        on_delete=models.PROTECT,
        verbose_name="Tipo de Contrato",
    )
    title = models.CharField("Titulo", max_length=50)
    message = models.TextField("Mensaje")
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
    op_release_date = models.DateField("Fecha de implementación")

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = "Solicitud de cambio de PO"
        verbose_name_plural = "Solicitudes de cambio de PO"


class ChangeOPRequestFile(models.Model):
    file = models.FileField("Archivo")
    change_op_request = models.ForeignKey(
        ChangeOPRequest,
        related_name="change_op_request_files",
        on_delete=models.PROTECT,
        verbose_name="Solicitud de cambio de Programa de Operación",
    )

    def __str__(self):
        return str(self.file)

    class Meta:
        verbose_name = "Archivo de solicitud de cambio de PO"
        verbose_name_plural = "Archivos de solicitud de cambio de PO"


class ChangeOPRequestMessage(models.Model):
    created_at = models.DateTimeField("Fecha de creación", default=timezone.now)
    creator = models.ForeignKey(
        User,
        related_name="change_op_request_messages",
        on_delete=models.PROTECT,
        blank=False,
        verbose_name="Creador",
    )
    message = models.TextField("Mensaje")

    def __str__(self):
        return str(self.message)

    class Meta:
        verbose_name = "Mensaje de solicitud de cambio de PO"
        verbose_name_plural = "Mensajes de solicitud de cambio de PO"


class ChangeOPRequestMessageFile(models.Model):
    file = models.FileField("Archivo")
    change_op_request_message = models.ForeignKey(
        ChangeOPRequestMessage,
        related_name="change_op_request_message_files",
        on_delete=models.PROTECT,
        verbose_name="Mensaje de solicitud de cambio de Programa de Operación",
    )

    def __str__(self):
        return str(self.file)

    class Meta:
        verbose_name = "Archivo asociado al mensaje de solicitud de cambio de PO"
        verbose_name_plural = (
            "Archivos asociados a mensaje de solicitud de cambio de PO"
        )


class StatusLog(models.Model):
    created_at = models.DateTimeField("Fecha de creación", default=timezone.now)
    previous_status = models.ForeignKey(
        ChangeOPRequestStatus,
        related_name="+",
        on_delete=models.PROTECT,
        verbose_name="Estado previo",
    )
    new_status = models.ForeignKey(
        ChangeOPRequestStatus,
        related_name="+",
        on_delete=models.PROTECT,
        verbose_name="Estado nuevo",
    )
    change_op_request = models.ForeignKey(
        ChangeOPRequest,
        related_name="+",
        on_delete=models.PROTECT,
        verbose_name="Solicitud de cambio de Programa de Operación",
    )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        verbose_name = "Log de estado"
        verbose_name_plural = "Logs de estado"


class OPChangeLog(models.Model):
    created_at = models.DateField("Fecha de creación", default=timezone.now)
    creator = models.ForeignKey(
        User,
        related_name="op_change_logs",
        on_delete=models.PROTECT,
        blank=False,
        verbose_name="Creador",
    )
    previous_op = models.ForeignKey(
        OperationProgram,
        related_name="+",
        on_delete=models.PROTECT,
        verbose_name="Programa de Operación previo",
    )
    new_op = models.ForeignKey(
        OperationProgram,
        related_name="+",
        on_delete=models.PROTECT,
        verbose_name="Nuevo Programa de Operación",
    )
    change_op_request = models.ForeignKey(
        ChangeOPRequest,
        related_name="op_change_logs",
        on_delete=models.PROTECT,
        verbose_name="Programa de Operación",
    )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        verbose_name = "Log de solicitud de cambio de PO"
        verbose_name_plural = "Logs de solicitud de cambio de PO"


class OPChangeDateLog(models.Model):
    user = models.ForeignKey(
        User,
        related_name="op_change_date_logs",
        on_delete=models.PROTECT,
        verbose_name="Usuario",
    )
    previous_data = models.JSONField("Datos anteriores")
    new_data = models.JSONField("Datos nuevos")
