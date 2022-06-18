from django.urls import reverse as reverse_url
from django.utils import timezone
from rest_framework import filters
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
)

from rest_api.models import OperationProgram, ChangeOPRequest, ChangeOPRequestStatus, ChangeOPProcessFile, \
    ChangeOPRequestLog
from rest_api.serializers import ChangeOPRequestSerializer, ChangeOPRequestStatusSerializer, \
    ChangeOPRequestDetailSerializer, ChangeOPRequestCreateSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class ChangeOPRequestStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows ChangeOPRequestStatus to be viewed.
    """

    pagination_class = StandardResultsSetPagination
    queryset = ChangeOPRequestStatus.objects.all().order_by("-name")
    serializer_class = ChangeOPRequestStatusSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["contract_type__name"]


class ChangeOPRequestViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                             mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows Change OP Request to be viewed, created and updated.
    """

    pagination_class = StandardResultsSetPagination
    queryset = ChangeOPRequest.objects.all().order_by("id")
    serializer_class = ChangeOPRequestSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "op__start_at",
        "id",
        "title",
        "reason",
    ]  # TODO: verificar si está filtrando por motivo

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = ChangeOPRequestSerializer(
            page, context={"request": request}, many=True
        )
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        # TODO: send email
        contract_type_id = request.data["contract_type"].split("/")[-2]
        if contract_type_id == "3":
            contract_type_id = "2"
        status_id = ChangeOPRequestStatus.objects.get(
            contract_type_id=contract_type_id, name="Evaluando admisibilidad"
        ).pk
        status_url = reverse_url(
            "changeoprequeststatus-detail", kwargs=dict(pk=status_id)
        )
        data = request.data.copy()
        data["status"] = status_url
        serializer = ChangeOPRequestCreateSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        change_op_request = serializer.save()
        errors = []
        try:
            files = request.FILES.getlist("files")
            for file in files:
                instance = ChangeOPProcessFile(
                    file=file, change_op_request_id=change_op_request.id
                )
                instance.save()
        except Exception as e:
            errors.append(e)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ChangeOPRequestDetailSerializer(
            instance, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=["put"], url_path="change-op")
    def change_op(self, request, *args, **kwargs):
        # TODO: send email
        obj = self.get_object()
        new_op_key = request.data.get("op")
        queryset = self.get_queryset()
        serializer = ChangeOPRequestSerializer(
            queryset, context={"request": request}, many=True
        )
        try:
            previous_op = obj.op
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
            obj.op = new_op
            obj.save()
            ChangeOPRequestLog.objects.create(
                created_at=timezone.now(), user=request.user, type=ChangeOPRequestLog.OP_CHANGE, change_op_request=obj,
                previous_data=dict(date=str(previous_op.start_at), type=previous_op.op_type.name),
                new_data=dict(date=str(new_op.start_at), type=new_op.op_type.name))
            return Response(serializer.data, status=HTTP_200_OK)
        except OperationProgram.DoesNotExist:
            raise NotFound()

    @action(detail=True, methods=["put"], url_path="change-status")
    def change_status(self, request, *args, **kwargs):
        obj = self.get_object()
        new_status_key = request.data.get("status")
        queryset = self.get_queryset()
        try:
            new_status = ChangeOPRequestStatus.objects.get(pk=new_status_key)
            previous_status = obj.status
            obj.status = new_status
            obj.save()
            ChangeOPRequestLog.objects.create(
                created_at=timezone.now(), user=request.user, type=ChangeOPRequestLog.STATUS_CHANGE,
                change_op_request=obj, previous_data=dict(value=previous_status), new_data=dict(value=new_status))
            serializer = ChangeOPRequestSerializer(queryset, context={"request": request}, many=True)
            return Response(serializer.data, status=HTTP_200_OK)
        except ChangeOPRequestStatus.DoesNotExist:
            raise NotFound()

    @action(detail=True, methods=["put"], url_path="change-reason")
    def change_reason(self, request, *args, **kwargs):
        obj = self.get_object()
        new_reason_key = request.data.get("reason")
        queryset = self.get_queryset()
        try:
            new_reason = new_reason_key
            previous_reason = obj.reason
            obj.reason = new_reason
            obj.save()
            ChangeOPRequestLog.objects.create(
                created_at=timezone.now(), user=request.user, type=ChangeOPRequestLog.REASON_CHANGE,
                change_op_request=obj, previous_data=dict(value=previous_reason), new_data=dict(value=new_reason))
            serializer = ChangeOPRequestSerializer(
                queryset, context={"request": request}, many=True
            )
            return Response(serializer.data, status=HTTP_200_OK)
        except Exception as e:
            print(e)
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
