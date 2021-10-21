from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class ContractType(models.Model):
    name = models.CharField("Nombre", max_length=5)

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

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Estado de Programa de Operación"
        verbose_name_plural = "Estados de Programa de Operación"


class OperationProgram(models.Model):
    start_at = models.DateField("Fecha de inicio", unique=True)
    op_type = models.ForeignKey(OperationProgramType, related_name="ops", on_delete=models.PROTECT,
                                verbose_name="Tipo de Programa de Operación")

    def __str__(self):
        return str(self.start_at)

    class Meta:
        verbose_name = "Programa de Operación"
        verbose_name_plural = "Programas de Operación"


class Organization(models.Model):
    name = models.CharField("Nombre", max_length=50)
    created_at = models.DateTimeField("Fecha de creación")
    op_type = models.ForeignKey(OperationProgramType, related_name="organizations", blank=False,
                                on_delete=models.PROTECT, verbose_name="Tipo de Programa de Operación")
    default_counterpart = models.ForeignKey("self", related_name="organizations", blank=True, on_delete=models.PROTECT,
                                            verbose_name="Contraparte por defecto")
    default_user_contact = models.ForeignKey("User", blank=True, related_name="organizations", on_delete=models.PROTECT,
                                             verbose_name="Usuario de contacto por defecto")

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"


class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_('Correo Electrónico'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, null=True, verbose_name="Organización")
    access_to_ops = models.BooleanField("Acceso a Programas de Operación", default=False)
    access_to_organizations = models.BooleanField("Acceso a Organizaciones", default=False)
    access_to_users = models.BooleanField("Acceso a Usuarios", default=False)


class ChangeOPRequest(models.Model):
    created_at = models.DateTimeField("Fecha de Creación", default=timezone.now)
    creator = models.ForeignKey(User, related_name="change_op_requests", on_delete=models.PROTECT, blank=False,
                                verbose_name="Creador")
    op = models.ForeignKey(OperationProgram, related_name="change_op_requests", on_delete=models.PROTECT,
                           verbose_name="Programa de Operación")
    status = models.ForeignKey(OperationProgramStatus, related_name="change_op_requests", on_delete=models.PROTECT,
                               verbose_name="Estado")
    counterpart = models.ForeignKey(Organization, related_name="change_op_request", on_delete=models.PROTECT,
                                    verbose_name="Contraparte")
    contract_type = models.ForeignKey(ContractType, related_name="change_op_request", on_delete=models.PROTECT,
                                      verbose_name="Tipo de Contrato")
    title = models.CharField("Titulo", max_length=50)
    message = models.TextField("Mensaje")
    updated_at = models.DateTimeField("Fecha de actualización", default=timezone.now)

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = "Solicitud de cambio de PO"
        verbose_name_plural = "Solicitudes de cambio de PO"


class ChangeOPRequestFile(models.Model):
    file = models.FileField("Archivo")
    change_op_request = models.ForeignKey(ChangeOPRequest, related_name="change_op_request_files",
                                          on_delete=models.PROTECT,
                                          verbose_name="Solicitud de cambio de Programa de Operación")

    def __str__(self):
        return str(self.file)

    class Meta:
        verbose_name = "Archivo de solicitud de cambio de PO"
        verbose_name_plural = "Archivos de solicitud de cambio de PO"


class ChangeOPRequestMessage(models.Model):
    created_at = models.DateTimeField("Fecha de creación", default=timezone.now)
    creator = models.ForeignKey(User, related_name="change_op_request_messages", on_delete=models.PROTECT, blank=False,
                                verbose_name="Creador")
    message = models.TextField("Mensaje")

    def __str__(self):
        return str(self.message)

    class Meta:
        verbose_name = "Mensaje de solicitud de cambio de PO"
        verbose_name_plural = "Mensajes de solicitud de cambio de PO"


class ChangeOPRequestMessageFile(models.Model):
    file = models.FileField("Archivo")
    change_op_request_message = models.ForeignKey(ChangeOPRequestMessage,
                                                  related_name="change_op_request_message_files",
                                                  on_delete=models.PROTECT,
                                                  verbose_name="Mensaje de solicitud de cambio de Programa de Operación")

    def __str__(self):
        return str(self.file)

    class Meta:
        verbose_name = "Archivo asociado al mensaje de solicitud de cambio de PO"
        verbose_name_plural = "Archivos asociados a mensaje de solicitud de cambio de PO"


class StatusLog(models.Model):
    created_at = models.DateTimeField("Fecha de creación", default=timezone.now)
    previous_status = models.ForeignKey(OperationProgramStatus, related_name="status_logs", on_delete=models.PROTECT,
                                        verbose_name="Estado previo")
    new_status = models.ForeignKey(OperationProgramStatus, related_name="+", on_delete=models.PROTECT,
                                   verbose_name="Estado nuevo")
    change_op_request = models.ForeignKey(ChangeOPRequest, related_name="+", on_delete=models.PROTECT,
                                          verbose_name="Solicitud de cambio de Programa de Operación")

    def __str__(self):
        return str(self.created_at)

    class Meta:
        verbose_name = "Log de estado"
        verbose_name_plural = "Logs de estado"


class OPChangeLog(models.Model):
    created_at = models.DateField("Fecha de creación", default=timezone.now)
    creator = models.ForeignKey(User, related_name="op_change_logs", on_delete=models.PROTECT, blank=False,
                                verbose_name="Creador")
    previous_op = models.ForeignKey(OperationProgram, related_name="+", on_delete=models.PROTECT,
                                    verbose_name="Programa de Operación previo")
    new_op = models.ForeignKey(OperationProgram, related_name="+", on_delete=models.PROTECT,
                               verbose_name="Nuevo Programa de Operación")
    change_op_request = models.ForeignKey(ChangeOPRequest, related_name="op_change_logs", on_delete=models.PROTECT,
                                          verbose_name="Programa de Operación")

    def __str__(self):
        return str(self.created_at)

    class Meta:
        verbose_name = "Log de solicitud de cambio de PO"
        verbose_name_plural = "Logs de solicitud de cambio de PO"
