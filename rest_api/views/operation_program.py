from django.utils import timezone
from rest_framework import filters
from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.status import HTTP_409_CONFLICT, HTTP_204_NO_CONTENT

from rest_api.exceptions import CustomValidation
from rest_api.models import OperationProgram, OperationProgramType, OPChangeLog, OperationProgramStatus
from rest_api.permissions import HasGroupPermission
from rest_api.serializers import OperationProgramSerializer, OperationProgramTypeSerializer, \
    OperationProgramDetailSerializer, OPChangeLogSerializer, OperationProgramStatusSerializer, \
    OperationProgramCreateSerializer


class OPChangeLogViewset(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows OPChangeLog to be viewed.
    """

    queryset = OPChangeLog.objects.all()
    serializer_class = OPChangeLogSerializer


class OperationProgramStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Operation Programs Status to be viewed.
    """

    queryset = OperationProgramStatus.objects.all().order_by("-name")
    serializer_class = OperationProgramStatusSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["contract_type__name"]


class OperationProgramViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Operation Programs to be viewed, created, updated and delete.
    Only can delete if does not exist a related ChangeOPRequest.
    """

    queryset = OperationProgram.objects.all().order_by("-start_at")
    serializer_class = OperationProgramSerializer
    permission_classes = [HasGroupPermission]
    required_groups = {
        "GET": ["Operation Program"],
        "POST": ["Operation Program"],
        "PUT": ["Operation Program"],
        "DELETE": ["Operation Program"],
    }

    def create(self, request, *args, **kwargs):
        self.serializer_class = OperationProgramCreateSerializer
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OperationProgramDetailSerializer(instance, context={"request": request})
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        object_key = kwargs.get("pk")
        try:
            operation_program = OperationProgram.objects.get(id=object_key)
            change_op_process = operation_program.change_op_processes.all().exists()
            change_op_request = operation_program.change_op_requests.all().exists()
            if change_op_process or change_op_request:
                raise CustomValidation(detail="Hay solicitudes de cambio asociadas al Programa de Operación",
                                       field="detail", status_code=HTTP_409_CONFLICT)
            self.perform_destroy(operation_program)
            return Response(status=HTTP_204_NO_CONTENT)
        except OperationProgram.DoesNotExist:
            raise NotFound()

    def update(self, request, *args, **kwargs):
        # TODO: send email
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        latest_op_change_log = OPChangeLog.objects.filter(operation_program=instance).order_by("-created_at").first()
        if latest_op_change_log:
            previous_data = latest_op_change_log.new_data
        else:
            previous_data = {"date": instance.start_at.isoformat(), "op_type": instance.op_type.name}

        # update records
        serializer = OperationProgramCreateSerializer(instance, context={"request": request}, data=request.data,
                                                      partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        new_data = previous_data.copy()
        new_data["date"] = instance.start_at.isoformat()
        new_data["op_type"] = instance.op_type.name
        try:
            OPChangeLog.objects.create(created_at=timezone.now(), user=request.user, previous_data=previous_data,
                                       new_data=new_data, operation_program=instance)
        except Exception as e:
            print(e)
        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class OperationProgramTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Operation Programs Type to be viewed.
    """

    queryset = OperationProgramType.objects.all().order_by("-name")
    serializer_class = OperationProgramTypeSerializer


class OPChangeLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows OPChangeLog to be viewed.
    """

    queryset = OPChangeLog.objects.all().order_by("-created_at")
    serializer_class = OPChangeLogSerializer
