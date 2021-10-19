from django.contrib.auth.models import AbstractUser

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
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


class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


class ContractType(models.Model):
    name = models.TextField("Nombre", max_length=5)


class OperationProgramType(models.Model):
    name = models.TextField("Nombre", max_length=10)


class OperationProgramStatus(models.Model):
    name = models.TextField("Nombre", max_length=50)
    time_threshold = models.IntegerField()


class OperationProgram(models.Model):
    start_at = models.DateField("Fecha de inicio", unique=True)
    op_type = models.ForeignKey(OperationProgramType, related_name="Tipo de programa de operación")


class Organization(models.Model):
    name = models.TextField("Nombre", max_length=30)
    created_at = models.DateTimeField()
    op_type = models.ForeignKey(OperationProgramType, related_name="Tipo de programa de operación", blank=False)
    default_counterpart = models.ForeignKey("self", related_name="Contraparte por defecto", blank=True)
    default_user_contact = models.ForeignKey(User, related_name='Usuario', blank=True)

