from django.core.management.base import BaseCommand
from django.utils import timezone

from rest_api.models import User
from rqworkers.models import SendMailJobExecution
from rqworkers.tasks import send_email_job


class Command(BaseCommand):
    help = 'async command to send emails'

    def add_arguments(self, parser):
        parser.add_argument('subject', help='email subject')
        parser.add_argument('body', help='email body')
        parser.add_argument('users', nargs='+', type=int, help='list of user ids. For instance: user_obj.pk ...')
        parser.add_argument('--sync', action='store_true', help='send email whithout worker')

    def handle(self, *args, **options):
        subject = options['subject']
        body = options['body']
        user_pk_list = options['users']
        sync = options['sync']

        job_execution_obj = SendMailJobExecution.objects.create(enqueueTimestamp=timezone.now(),
                                                                status=SendMailJobExecution.ENQUEUED,
                                                                subject=subject, body=body)
        for user in User.objects.filter(pk__in=user_pk_list):
            job_execution_obj.users.add(user)

        if sync:
            send_email_job(job_execution_obj.pk)
        else:
            send_email_job.delay(job_execution_obj.pk)
