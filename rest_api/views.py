from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse as reverse_url
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import filters
from rest_framework import mixins, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_409_CONFLICT,
    HTTP_204_NO_CONTENT,
    HTTP_201_CREATED,
)

from rest_api.exceptions import CustomValidation
from rest_api.models import (
    User,
    OperationProgram,
    OperationProgramType,
    Organization,
    ContractType,
    ChangeOPRequest,
    ChangeOPRequestStatus,
    OPChangeDataLog,
    OPChangeLog,
    StatusLog,
    ChangeOPRequestMessage,
    ChangeOPRequestFile,
    ChangeOPRequestMessageFile,
    OperationProgramStatus,
)
from rest_api.permissions import HasGroupPermission
from rest_api.serializers import (
    UserSerializer,
    UserLoginSerializer,
    UserTokenSerializer,
    OperationProgramSerializer,
    OperationProgramTypeSerializer,
    OrganizationSerializer,
    ContractTypeSerializer,
    ChangeOPRequestSerializer,
    ChangeOPRequestStatusSerializer,
    OperationProgramDetailSerializer,
    OPChangeDataLogSerializer,
    ChangeOPRequestDetailSerializer,
    ChangeOPRequestMessageSerializer,
    OPChangeLogSerializer,
    StatusLogSerializer,
    ChangeOPRequestFileSerializer,
    ChangeOPRequestMessageFileSerializer,
    CreateChangeOPRequestMessageSerializer,
    OperationProgramStatusSerializer,
    ChangeOPRequestCreateSerializer,
    OrganizationCreateSerializer,
    OperationProgramCreateSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed, created, updated and delete.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [HasGroupPermission]
    required_groups = {
        "GET": ["User"],
        "POST": ["User"],
        "PUT": ["User"],
        "DELETE": ["User"],
    }

    def destroy(self, request, *args, **kwargs):
        object_key = kwargs.get("pk")
        try:
            user = get_user_model().objects.get(id=object_key)
            user_has_reverse = False
            for reverse in [
                f for f in user._meta.get_fields() if f.auto_created and not f.concrete
            ]:
                name = reverse.get_accessor_name()
                has_reverse_one_to_one = reverse.one_to_one and hasattr(user, name)
                has_reverse_other = (
                    not reverse.one_to_one and getattr(user, name).count()
                )
                if has_reverse_one_to_one or has_reverse_other:
                    user_has_reverse = True

            if user_has_reverse:
                raise CustomValidation(
                    detail="El usuario se encuentra asociado a otro registro en la base de datos.",
                    field="detail",
                    status_code=HTTP_409_CONFLICT,
                )
            self.perform_destroy(user)
            return Response(status=HTTP_204_NO_CONTENT)
        except get_user_model().DoesNotExist:
            raise NotFound()

    @action(detail=True, methods=["put"])
    def change_password(self, request, *args, **kwargs):
        user = self.get_object()
        new_password = request.data.get("password")
        queryset = self.get_queryset()
        try:
            user.set_password(new_password)
            user.save()
            serializer = UserSerializer(
                queryset, context={"request": request}, many=True
            )
            return Response(serializer.data, status=HTTP_200_OK)
        except User.DoesNotExist:
            raise NotFound()


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
        serializer = OperationProgramDetailSerializer(
            instance, context={"request": request}
        )
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        object_key = kwargs.get("pk")
        try:
            operation_program = OperationProgram.objects.get(id=object_key)
            change_op_request = operation_program.change_op_requests.all()
            if change_op_request:
                raise CustomValidation(
                    detail="Hay solicitudes de cambio asociadas al Programa de Operación",
                    field="detail",
                    status_code=HTTP_409_CONFLICT,
                )
            self.perform_destroy(operation_program)
            return Response(status=HTTP_204_NO_CONTENT)
        except OperationProgram.DoesNotExist:
            raise NotFound()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        op_change_data_logs = (
            OPChangeDataLog.objects.all().filter(op=instance).order_by("-created_at")
        )
        if op_change_data_logs:
            previous_data = op_change_data_logs[0].new_data
        else:
            previous_data = {
                "date": instance.start_at.isoformat(),
                "op_type": instance.op_type.name,
            }
        serializer = OperationProgramCreateSerializer(
            instance, context={"request": request}, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        new_data = previous_data.copy()
        new_data["date"] = instance.start_at.isoformat()
        new_data["op_type"] = instance.op_type.name
        try:
            OPChangeDataLog.objects.create(
                created_at=timezone.now(),
                user=request.user,
                previous_data=previous_data,
                new_data=new_data,
                op=instance,
            )
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


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Organizations to be viewed, created, updated and delete.
    Only can delete if does not exist a related User.
    """

    queryset = Organization.objects.all().order_by("-name")
    serializer_class = OrganizationSerializer
    permission_classes = [HasGroupPermission]

    required_groups = {
        "POST": ["Organization"],
        "PUT": ["Organization"],
        "DELETE": ["Organization"],
    }

    def create(self, request, *args, **kwargs):
        self.serializer_class = OrganizationCreateSerializer
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        object_key = kwargs.get("pk")
        try:
            organization = Organization.objects.get(id=object_key)
            users = organization.user_set.all()
            if users:
                raise CustomValidation(
                    detail="Hay usuarios asociados a la Organización",
                    field="detail",
                    status_code=HTTP_409_CONFLICT,
                )
            self.perform_destroy(organization)
            return Response(status=HTTP_204_NO_CONTENT)
        except Organization.DoesNotExist:
            raise NotFound()


class ContractTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Contract Type to be viewed.
    """

    queryset = ContractType.objects.all().order_by("-name")
    serializer_class = ContractTypeSerializer


class OPChangeDataLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows OPChangeDataLog to be viewed.
    """

    queryset = OPChangeDataLog.objects.all().order_by("-created_at")
    serializer_class = OPChangeDataLogSerializer


class ChangeOPRequestStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows ChangeOPRequestStatus to be viewed.
    """

    queryset = ChangeOPRequestStatus.objects.all().order_by("-name")
    serializer_class = ChangeOPRequestStatusSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["contract_type__name"]


class ChangeOPRequestMessageViewSet(
    viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin
):
    """
    API endpoint that allows ChangeOPRequestMessage to be viewed.
    """

    queryset = ChangeOPRequestMessage.objects.all().order_by("-created_at")
    serializer_class = ChangeOPRequestMessageSerializer

    def create(self, request, *args, **kwargs):

        serializer = CreateChangeOPRequestMessageSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        change_op_request_message = serializer.save()
        errors = []
        try:
            files = request.FILES.getlist("files")
            for file in files:
                instance = ChangeOPRequestMessageFile(
                    file=file, change_op_request_message_id=change_op_request_message.id
                )
                instance.save()
        except Exception as e:
            errors.append(e)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)


class OPChangeLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows OPChangeLog to be viewed.
    """

    queryset = OPChangeLog.objects.all().order_by("-created_at")
    serializer_class = OPChangeLogSerializer


class StatusLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows StatusLog to be viewed.
    """

    queryset = StatusLog.objects.all().order_by("-created_at")
    serializer_class = StatusLogSerializer


class ChangeOPRequestFileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows StatusLog to be viewed.
    """

    queryset = StatusLog.objects.all().order_by("-created_at")
    serializer_class = StatusLogSerializer


class ChangeOPRequestViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint that allows Change OP Request to be viewed, created and updated.
    """

    queryset = ChangeOPRequest.objects.all().order_by("-created_at")
    serializer_class = ChangeOPRequestSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["op__start_at", "id", "title", "reason"]

    def list(self, request, *args, **kwargs):
        user = request.user
        user_organization = user.organization
        queryset = self.filter_queryset(self.get_queryset()).filter(
            Q(counterpart=user_organization)
            | Q(creator__organization=user_organization)
        )
        page = self.paginate_queryset(queryset)
        serializer = ChangeOPRequestSerializer(
            page, context={"request": request}, many=True
        )
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
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
                instance = ChangeOPRequestFile(
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
        obj = self.get_object()
        new_op_key = request.data.get("op")
        update_deadlines = request.data.get("update_deadlines")
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
                change_op_request=obj,
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
            new_status = ChangeOPRequestStatus.objects.get(pk=new_status_key)
            previous_status = obj.status
            obj.status = new_status
            obj.save()
            status_log = StatusLog(
                created_at=timezone.now(),
                user=request.user,
                previous_status=previous_status,
                new_status=new_status,
                change_op_request=obj,
            )
            status_log.save()
            serializer = ChangeOPRequestSerializer(
                queryset, context={"request": request}, many=True
            )
            return Response(serializer.data, status=HTTP_200_OK)
        except ChangeOPRequestStatus.DoesNotExist:
            raise NotFound()


class OPChangeDataLogViewset(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows OPChangeDataLog to be viewed.
    """

    queryset = OPChangeDataLog.objects.all()
    serializer_class = OPChangeDataLogSerializer


class ChangeOPRequestFileViewset(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows ChangeOPRequestFile to be viewed.
    """

    queryset = ChangeOPRequestFile.objects.all()
    serializer_class = ChangeOPRequestFileSerializer


class ChangeOPRequestMessageFileViewset(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows ChangeOPRequestMessageFileViewset to be viewed.
    """

    queryset = ChangeOPRequestMessageFile.objects.all()
    serializer_class = ChangeOPRequestMessageFileSerializer


class OperationProgramStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Operation Programs Status to be viewed.
    """

    queryset = OperationProgramStatus.objects.all().order_by("-name")
    serializer_class = OperationProgramStatusSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["contract_type__name"]


@api_view(["GET"])
@permission_classes((AllowAny,))
def change_op_request_reasons(request):
    """
    API endpoint that allows Operation Programs Request Reasons to be viewed.
    """

    data = ChangeOPRequest.REASON_CHOICES

    return JsonResponse({"options": data}, status=HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    login_serializer = UserLoginSerializer(data=request.data)
    data = login_serializer.is_valid()
    if not data:
        raise AuthenticationFailed()
    user = login_serializer.context["user"]
    model_user = User.objects.get(email=user)
    model_user.last_login = timezone.now()
    model_user.save()
    user_data = UserSerializer(model_user, context={"request": request}).data
    token, _ = Token.objects.get_or_create(user=login_serializer.context["user"])
    user_data.update({"token": token.key, "error": None})
    return JsonResponse(user_data, status=HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def verify(request):
    user = str(request.user)
    token = str(request.auth)
    data = {"email": user, "token": token}
    token_serializer = UserTokenSerializer(data=data)
    data = token_serializer.is_valid()
    if not data:
        raise AuthenticationFailed()
    model_user = User.objects.get(email=user)
    user_data = UserSerializer(model_user, context={"request": request}).data
    user_data.update({"token": token, "error": None})
    return JsonResponse(user_data, status=HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def send_email(request):
    subject = "test"
    body = """
    Hola, este es un mensaje de prueba
    """
    users = User.objects.all()
    call_command("sendemail", "--sync", subject, body, *[user.pk for user in users])

    return JsonResponse({"user": str(request.user)}, status=HTTP_200_OK)
