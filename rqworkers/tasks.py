import time
from smtplib import SMTPException

from django.core.mail import send_mail
from django.utils import timezone
from django_rq import job
from rq import get_current_job

from rqworkers.models import SendMailJobExecution


@job('email_sender')
def send_email_job(user_list, subject, body):
    job_execution_obj = SendMailJobExecution.objects.create(enqueueTimestamp=timezone.now(),
                                                            status=SendMailJobExecution.ENQUEUED,
                                                            subject=subject, body=body)
    for user in user_list:
        job_execution_obj.users.add(user)

    job_execution_obj.status = SendMailJobExecution.RUNNING
    job_execution_obj.executionStart = timezone.now()
    job_execution_obj.save()

    sender = 'noreply@mg.adatrap.cl'

    try:
        for user in user_list:
            send_mail(subject, body, sender, [user.email])
            job_execution_obj.status = SendMailJobExecution.FINISHED
    except SMTPException as e:
        job_execution_obj.status = SendMailJobExecution.FAILED
        job_execution_obj.errorMessage = str(e)

    job_execution_obj.executionEnd = timezone.now()
    job_execution_obj.seen = False
    job_execution_obj.save()
