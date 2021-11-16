from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import mixins, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_409_CONFLICT, HTTP_204_NO_CONTENT
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


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
        "GET": ["Organization"],
        "POST": ["Organization"],
        "PUT": ["Organization"],
        "DELETE": ["Organization"],
    }

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


class ChangeOPRequestStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows ChangeOPRequestStatus to be viewed.
    """

    queryset = ChangeOPRequestStatus.objects.all().order_by("-name")
    serializer_class = ChangeOPRequestStatusSerializer


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
    search_fields = ["op__start_at"]

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

    @action(detail=True, methods=["put"])
    def change_op(self, request, *args, **kwargs):
        obj = self.get_object()
        new_op_key = request.data.get("op")
        queryset = self.get_queryset()
        serializer = ChangeOPRequestSerializer(
            queryset, context={"request": request}, many=True
        )
        try:
            new_op = OperationProgram.objects.get(pk=new_op_key)
            previous_op = obj.op
            if new_op_key == previous_op.pk:
                return Response(serializer.data, status=HTTP_200_OK)
            obj.op = new_op
            obj.save()
            op_change_log = OPChangeLog(
                created_at=timezone.now(),
                creator=request.user,
                previous_op=previous_op,
                new_op=new_op,
                change_op_request=obj,
            )
            op_change_log.save()
            return Response(serializer.data, status=HTTP_200_OK)
        except OperationProgram.DoesNotExist:
            raise NotFound()

    @action(detail=True, methods=["put"])
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
