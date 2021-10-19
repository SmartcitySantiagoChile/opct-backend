from django.db import models

from rest_api.models import User


class JobExecution(models.Model):
    """ record about async execution """
    jobId = models.UUIDField('Identificador de trabajo', null=True)
    enqueueTimestamp = models.DateTimeField('Encolado')
    # time when execution started
    executionStart = models.DateTimeField('Inicio', null=True)
    # time when execution finished
    executionEnd = models.DateTimeField('Fin', null=True)
    ENQUEUED = 'enqueued'
    RUNNING = 'running'
    FINISHED = 'finished'
    FAILED = 'failed'
    CANCELED = 'canceled'
    EXPIRED = 'expired'
    STATUS_CHOICES = (
        (ENQUEUED, 'Encolado'),
        (RUNNING, 'Cargando datos'),
        (FINISHED, 'Finalización exitosa'),
        (FAILED, 'Finalización con error'),
        (CANCELED, 'Cancelado por usuario'),
        (EXPIRED, 'Vencido')
    )
    # state of execution
    status = models.CharField('Estado', max_length=10, choices=STATUS_CHOICES)
    # for stack trace
    errorMessage = models.TextField('Mensaje de error', max_length=500, null=False, default="")

    def get_dictionary(self):
        return {
            'jobId': self.jobId,
            'enqueueTimestamp': self.enqueueTimestamp,
            'executionStart': self.executionStart,
            'executionEnd': self.executionEnd,
            'status': self.status,
            'statusName': self.get_status_display(),
            'error': self.errorMessage
        }

    class Meta:
        abstract = True


class SendMailJobExecution(JobExecution):
    """ Record about async execution for send email."""
    # users who will receive the email
    users = models.ManyToManyField(User, verbose_name='Lista de Usuarios')
    # email subject
    subject = models.TextField(verbose_name='Asunto')
    # email body
    body = models.TextField(verbose_name='Cuerpo del mensaje')

    class Meta:
        verbose_name = 'Trabajo para enviar correo'
        verbose_name_plural = 'Trabajos para enviar correos'
