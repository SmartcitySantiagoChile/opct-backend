import logging

from django.db import transaction
from django.db.models import Q, Count
from django.utils import timezone
from rest_framework import filters
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ParseError, ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from rest_api.models import OperationProgram, ChangeOPRequest, ChangeOPRequestStatus, \
    ChangeOPProcessMessage, ChangeOPProcessMessageFile, ChangeOPProcess, ChangeOPProcessStatus, \
    ChangeOPProcessLog, OPChangeLog
from rest_api.serializers import OPChangeLogSerializer, ChangeOPProcessMessageSerializer, \
    CreateChangeOPProcessMessageSerializer, ChangeOPProcessMessageFileSerializer, ChangeOPProcessSerializer, \
    ChangeOPProcessStatusSerializer, ChangeOPProcessDetailSerializer, ChangeOPProcessCreateSerializer, \
    ChangeOPProcessLogSerializer, ChangeOPRequestCreateWithStatusAndOPSerializer

logger = logging.getLogger(__name__)


class ChangeOPProcessViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    """
    API endpoint that allows Change OP Process to be viewed, created and updated.
    """
    queryset = ChangeOPProcess.objects.order_by("-created_at")
    filter_backends = [filters.SearchFilter]
    search_fields = ["operation_program__start_at", "id", "title"]

    # TODO: verificar si está filtrando por motivo
    def get_queryset(self):
        queryset = ChangeOPProcess.objects.order_by("-created_at")
        user = self.request.user
        user_organization = user.organization
        queryset = self.filter_queryset(queryset).filter(
            Q(counterpart=user_organization) | Q(creator__organization=user_organization))

        if self.action == 'list':
            return queryset.annotate(change_op_requests_count=Count('change_op_requests'))
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChangeOPProcessDetailSerializer
        elif self.action == 'create':
            return ChangeOPProcessCreateSerializer
        else:
            return ChangeOPProcessSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # TODO: send email

        return response

    @action(detail=True, methods=["put"], url_path="change-op")
    def change_op(self, request, *args, **kwargs):
        # TODO: send email
        obj = self.get_object()
        new_operation_program_key = request.data.get("operation_program", None)
        update_deadlines = request.data.get("update_deadlines", False)
        queryset = self.get_queryset()
        serializer = ChangeOPProcessSerializer(queryset, context={"request": request}, many=True)

        previous_operation_program = obj.operation_program

        if new_operation_program_key is None:
            new_operation_program = None
            new_log_data = dict(date='', type='', update_deadlines=False)
            new_op_release_date = None
        else:
            try:
                new_operation_program = OperationProgram.objects.get(pk=new_operation_program_key)
                new_log_data = dict(date=str(new_operation_program.start_at), type=new_operation_program.op_type.name,
                                    update_deadlines=update_deadlines)
                new_op_release_date = new_operation_program.start_at
            except OperationProgram.DoesNotExist:
                raise NotFound()
        if previous_operation_program is not None and new_operation_program_key == previous_operation_program.pk:
            return Response(serializer.data, status=HTTP_200_OK)

        obj.operation_program = new_operation_program
        obj.op_release_date = new_op_release_date
        if update_deadlines:
            log_type = ChangeOPProcessLog.OP_CHANGE_WITH_DEADLINE_UPDATED
        else:
            log_type = ChangeOPProcessLog.OP_CHANGE
        obj.save()

        previous_data = dict(date='', type='')
        if previous_operation_program is not None:
            previous_data = dict(date=str(previous_operation_program.start_at),
                                 type=previous_operation_program.op_type.name)
        ChangeOPProcessLog.objects.create(
            created_at=timezone.now(), user=request.user, change_op_process=obj, type=log_type,
            previous_data=previous_data,
            new_data=new_log_data)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(detail=True, methods=["put"], url_path="change-status")
    def change_status(self, request, *args, **kwargs):
        obj = self.get_object()
        new_status_key = request.data.get("status", None)
        queryset = self.get_queryset()
        try:
            new_status = ChangeOPProcessStatus.objects.get(pk=new_status_key)
            previous_status = obj.status
            obj.status = new_status
            obj.save()
            ChangeOPProcessLog.objects.create(created_at=timezone.now(), user=request.user,
                                              type=ChangeOPProcessLog.STATUS_CHANGE,
                                              previous_data=dict(value=previous_status.name),
                                              new_data=dict(value=new_status.name), change_op_process=obj)
            serializer = ChangeOPProcessSerializer(queryset, context={"request": request}, many=True)
            return Response(serializer.data, status=HTTP_200_OK)
        except ChangeOPProcessStatus.DoesNotExist:
            raise NotFound()

    @action(detail=True, methods=["post"])
    def add_message(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            with transaction.atomic():
                message = request.data.get("message")
                files = request.FILES.getlist("files")
                related_requests = request.data.getlist("related_requests", [])
                if len(related_requests) == 0:
                    raise ValidationError('Mensaje debe estar relacionado a una o más solicitudes de modificación')
                if message == "" and len(files) == 0:
                    raise ValidationError('Mensaje no puede ser vacío')

                message_obj = ChangeOPProcessMessage.objects.create(creator=request.user, message=message,
                                                                    change_op_process=obj)
                for file in files:
                    ChangeOPProcessMessageFile.objects.create(filename=file.name, file=file,
                                                              change_op_process_message=message_obj)
                for related_request in related_requests:
                    change_op_request_obj = ChangeOPRequest.objects.get(change_op_process=obj, pk=related_request)
                    message_obj.related_requests.add(change_op_request_obj)
        except (ValidationError, ChangeOPRequest.DoesNotExist) as e:
            logger.error(e)
            raise ParseError(detail=str(e))

        return Response(None, status=HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="create-change-op-request")
    def create_change_op_request(self, request, *args, **kwargs):
        obj = self.get_object()
        change_op_request = request.data.get("change_op_request")
        try:
            change_op_request.pop('id')
            related_requests = change_op_request.pop('related_requests')

            serializer = ChangeOPRequestCreateWithStatusAndOPSerializer(data=change_op_request)
            serializer.is_valid(raise_exception=True)
            copr = serializer.save(creator=request.user, change_op_process=obj)

            copr.related_requests.set(related_requests)
            operation_program_data = dict(date="", type="")
            if copr.operation_program:
                operation_program_data = dict(date=copr.operation_program.start_at.strftime('%d-%m-%Y'),
                                              type=copr.operation_program.op_type.name)
            ChangeOPProcessLog.objects.create(created_at=timezone.now(), user=request.user,
                                              type=ChangeOPProcessLog.CHANGE_OP_REQUEST_CREATION,
                                              previous_data=dict(),
                                              new_data=dict(title=copr.title, reason=copr.reason,
                                                            related_routes=copr.related_routes,
                                                            operation_program=operation_program_data,
                                                            status=copr.status.name),
                                              change_op_process=obj)

            return Response(None, status=HTTP_200_OK)
        except ChangeOPRequestStatus.DoesNotExist:
            raise NotFound()

    @action(detail=True, methods=["put", "patch"], url_path="update-change-op-requests")
    def update_change_op_requests(self, request, *args, **kwargs):
        obj = self.get_object()
        change_op_requests = request.data.get("change_op_requests")

        for change_op_request in change_op_requests:
            print(change_op_request)

        # ChangeOPRequestLog.objects.create()

    @action(detail=True, methods=["put"], url_path="change-related-requests")
    def change_related_requests(self, request, *args, **kwargs):
        obj = self.get_object()
        new_requests = request.data.get("related_requests")
        try:
            obj.related_requests.clear()
            for request in new_requests:
                request_object = ChangeOPRequest.objects.get(id=request)
                obj.related_requests.add(request_object)
            obj.save()
            return Response(None, status=HTTP_200_OK)
        except ChangeOPRequestStatus.DoesNotExist:
            raise NotFound()


class ChangeOPProcessMessageFileViewset(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows ChangeOPProcessMessageFile to be viewed.
    """

    queryset = ChangeOPProcessMessageFile.objects.all()
    serializer_class = ChangeOPProcessMessageFileSerializer


class ChangeOPProcessLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows ChangeOPProcessLog to be viewed.
    """
    queryset = ChangeOPProcessLog.objects.all().order_by("-created_at")
    serializer_class = ChangeOPProcessLogSerializer


class OPChangeLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows OPChangeLog to be viewed.
    """

    queryset = OPChangeLog.objects.all().order_by("-created_at")
    serializer_class = OPChangeLogSerializer


class ChangeOPProcessStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows ChangeOPRequestStatus to be viewed.
    """

    queryset = ChangeOPProcessStatus.objects.all().order_by("-name")
    serializer_class = ChangeOPProcessStatusSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["contract_type__name"]


class ChangeOPProcessMessageViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin):
    """
    API endpoint that allows ChangeOPRequestMessage to be viewed.
    """

    queryset = ChangeOPProcessMessage.objects.all().order_by("-created_at")
    serializer_class = ChangeOPProcessMessageSerializer

    def create(self, request, *args, **kwargs):
        # TODO: no se usa, fue reemplazado por una acción en el viewset de changeOPProcess
        serializer = CreateChangeOPProcessMessageSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        change_op_process_message = serializer.save()
        errors = []
        try:
            files = request.FILES.getlist("files")
            for file in files:
                ChangeOPProcessMessageFile.objects.create(filename=file.name, file=file,
                                                          change_op_process_message=change_op_process_message)
        except Exception as e:
            errors.append(e)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)
