from django.db.models import Q
from django.urls import reverse as reverse_url
from django.utils import timezone
from rest_framework import filters
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
)

from rest_api.models import (
    OperationProgram,
    ChangeOPRequest,
    ChangeOPRequestStatus,
    OPChangeLog,
    ChangeOPProcessMessage,
    ChangeOPProcessFile,
    ChangeOPProcessMessageFile,
    ChangeOPProcess,
    ChangeOPProcessStatus,
    ChangeOPProcessStatusLog,
)
from rest_api.serializers import (
    OPChangeLogSerializer,
    ChangeOPRequestCreateSerializer,
    ChangeOPProcessMessageSerializer,
    CreateChangeOPProcessMessageSerializer,
    ChangeOPProcessFileSerializer,
    ChangeOPProcessMessageFileSerializer,
    ChangeOPProcessSerializer,
    ChangeOPProcessStatusSerializer,
    ChangeOPProcessDetailSerializer,
    ChangeOPProcessStatusLogSerializer,
    ChangeOPProcessCreateSerializer,
)


class ChangeOPProcessViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint that allows Change OP Process to be viewed, created and updated.
    """

    queryset = ChangeOPProcess.objects.all().order_by("-created_at")
    serializer_class = ChangeOPProcessSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "op__start_at",
        "id",
        "title",
    ]  # TODO: verificar si está filtrando por motivo

    def list(self, request, *args, **kwargs):
        user = request.user
        user_organization = user.organization
        queryset = self.filter_queryset(self.get_queryset()).filter(
            Q(counterpart=user_organization)
            | Q(creator__organization=user_organization)
        )
        page = self.paginate_queryset(queryset)
        serializer = ChangeOPProcessSerializer(
            page, context={"request": request}, many=True
        )
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        print(request.data["base_op"])
        # TODO: send email
        contract_type_id = request.data["contract_type"].split("/")[-2]
        if contract_type_id == "3":
            contract_type_id = "2"
        status_id = ChangeOPProcessStatus.objects.get(
            contract_type_id=contract_type_id, name="Evaluando admisibilidad"
        ).pk
        status_url = reverse_url(
            "changeopprocessstatus-detail", kwargs=dict(pk=status_id)
        )
        data = request.data.copy()
        data["status"] = status_url
        serializer = ChangeOPProcessCreateSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        change_op_process = serializer.save()
        errors = []
        try:
            files = request.FILES.getlist("files")
            for file in files:
                instance = ChangeOPProcessFile(
                    file=file, change_op_process_id=change_op_process.id
                )
                instance.save()
        except Exception as e:
            errors.append(e)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ChangeOPProcessDetailSerializer(
            instance, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=["put"], url_path="change-op")
    def change_op(self, request, *args, **kwargs):
        # TODO: send email
        obj = self.get_object()
        new_op_key = request.data.get("op")
        update_deadlines = request.data.get("update_deadlines")
        queryset = self.get_queryset()
        serializer = ChangeOPProcessSerializer(
            queryset, context={"request": request}, many=True
        )
        try:
            previous_op = obj.base_op
            if new_op_key:
                new_op = OperationProgram.objects.get(pk=new_op_key)
            else:
                new_op = new_op_key
                obj.op_release_date = new_op_key
            if previous_op:
                if new_op_key == previous_op.pk:
                    return Response(serializer.data, status=HTTP_200_OK)
            else:
                if new_op_key == previous_op:
                    return Response(serializer.data, status=HTTP_200_OK)
            obj.base_op = new_op
            if update_deadlines:
                obj.op_release_date = new_op.start_at
            else:
                update_deadlines = False
            obj.save()
            op_change_log = OPChangeLog(
                created_at=timezone.now(),
                creator=request.user,
                previous_op=previous_op,
                new_op=new_op,
                change_op_process=obj,
                update_deadlines=update_deadlines,
            )
            op_change_log.save()
            return Response(serializer.data, status=HTTP_200_OK)
        except OperationProgram.DoesNotExist:
            raise NotFound()

    @action(detail=True, methods=["put"], url_path="change-status")
    def change_status(self, request, *args, **kwargs):
        obj = self.get_object()
        new_status_key = request.data.get("status")
        queryset = self.get_queryset()
        try:
            new_status = ChangeOPProcessStatus.objects.get(pk=new_status_key)
            previous_status = obj.status
            obj.status = new_status
            obj.save()
            change_op_process_status_log = ChangeOPProcessStatusLog(
                created_at=timezone.now(),
                user=request.user,
                previous_status=previous_status,
                new_status=new_status,
                change_op_process=obj,
            )
            change_op_process_status_log.save()
            serializer = ChangeOPProcessSerializer(
                queryset, context={"request": request}, many=True
            )
            return Response(serializer.data, status=HTTP_200_OK)
        except ChangeOPProcessStatus.DoesNotExist:
            raise NotFound()

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


class ChangeOPProcessFileViewset(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows ChangeOPProcessFile to be viewed.
    """

    queryset = ChangeOPProcessFile.objects.all()
    serializer_class = ChangeOPProcessFileSerializer


class ChangeOPProcessMessageFileViewset(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows ChangeOPProcessMessageFile to be viewed.
    """

    queryset = ChangeOPProcessMessageFile.objects.all()
    serializer_class = ChangeOPProcessMessageFileSerializer


class ChangeOPProcessStatusLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows ChangeOPProcessStatusLog to be viewed.
    """

    queryset = ChangeOPProcessStatusLog.objects.all().order_by("-created_at")
    serializer_class = ChangeOPProcessStatusLogSerializer


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


class ChangeOPProcessMessageViewSet(
    viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin
):
    """
    API endpoint that allows ChangeOPRequestMessage to be viewed.
    """

    queryset = ChangeOPProcessMessage.objects.all().order_by("-created_at")
    serializer_class = ChangeOPProcessMessageSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateChangeOPProcessMessageSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        change_op_process_message = serializer.save()
        errors = []
        try:
            files = request.FILES.getlist("files")
            for file in files:
                instance = ChangeOPProcessMessageFile(
                    file=file, change_op_process_message_id=change_op_process_message.id
                )
                instance.save()
        except Exception as e:
            errors.append(e)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)
