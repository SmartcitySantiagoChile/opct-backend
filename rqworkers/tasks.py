from smtplib import SMTPException

from django.core.mail import send_mail
from django.utils import timezone
from django_rq import job

from rqworkers.models import SendMailJobExecution


@job('email_sender')
def send_email_job(job_execution_pk):
    job_execution_obj = SendMailJobExecution.objects.get(pk=job_execution_pk)
    job_execution_obj.status = SendMailJobExecution.RUNNING
    job_execution_obj.executionStart = timezone.now()
    job_execution_obj.save()

    email_list = [user.email for user in job_execution_obj.users.all()]
    try:
        send_mail(job_execution_obj.subject, job_execution_obj.body, None, email_list)
        job_execution_obj.status = SendMailJobExecution.FINISHED
    except SMTPException as e:
        job_execution_obj.status = SendMailJobExecution.FAILED
        job_execution_obj.errorMessage = str(e)

    job_execution_obj.executionEnd = timezone.now()
    job_execution_obj.seen = False
    job_execution_obj.save()
