from django.contrib.auth.models import Group
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import mixins, viewsets
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_409_CONFLICT, HTTP_204_NO_CONTENT

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
)
from rest_api.permissions import HasGroupPermission
from rest_api.serializers import (
    UserSerializer,
    GroupSerializer,
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
from rqworkers.tasks import send_email_job


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


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed, created, updated and delete.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


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


class OperationProgramTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Operation Programs Type to be viewed, created, updated and delete.
    """

    queryset = OperationProgramType.objects.all()
    serializer_class = OperationProgramTypeSerializer
    permission_classes = [HasGroupPermission, IsAdminUser]

    required_groups = {
        "GET": ["Operation Program"],
        "POST": ["Operation Program"],
        "PUT": ["Operation Program"],
        "DELETE": ["Operation Program"],
    }


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


class ContractTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Contract Type to be viewed, created, updated and delete.
    """

    queryset = ContractType.objects.all()
    serializer_class = ContractTypeSerializer
    permission_classes = [IsAdminUser]


class ChangeOPRequestStatusViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ChangeOPRequestStatus to be viewed, created, updated and delete.
    """

    queryset = ChangeOPRequestStatus.objects.all()
    serializer_class = ChangeOPRequestStatusSerializer
    permission_classes = [IsAdminUser]


class ChangeOPRequestViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint that allows Change OP Request to be viewed, created, updated and delete.
    """

    queryset = ChangeOPRequest.objects.all().order_by("-created_at")
    serializer_class = ChangeOPRequestSerializer
    permission_classes = [HasGroupPermission]

    required_groups = {
        "GET": ["Operation Program"],
        "POST": ["Operation Program"],
        "PUT": ["Operation Program"],
    }

    def list(self, request, *args, **kwargs):
        user = request.user
        user_organization = user.organization
        queryset = self.get_queryset().filter(
            Q(counterpart=user_organization) | Q(creator=user)
        )
        serializer = ChangeOPRequestSerializer(
            queryset, context={"request": request}, many=True
        )
        return Response(serializer.data)


class OPChangeDataLogViewset(viewsets.ModelViewSet):
    """
    API endpoint that allows OPChangeDataLog to be viewed, created, updated and delete.
    """

    queryset = OPChangeDataLog.objects.all()
    serializer_class = OPChangeDataLogSerializer
    permission_classes = [HasGroupPermission]
    required_groups = {
        "GET": ["Operation Program"],
        "POST": ["Operation Program"],
        "PUT": ["Operation Program"],
        "DELETE": ["Operation Program"],
    }


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    login_serializer = UserLoginSerializer(data=request.data)
    data = login_serializer.is_valid()
    if not data:
        raise AuthenticationFailed()
    user = login_serializer.context["user"]
    token, _ = Token.objects.get_or_create(user=login_serializer.context["user"])
    return JsonResponse(
        {"user": str(user), "token": token.key, "error": None}, status=HTTP_200_OK
    )


@csrf_exempt
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
    return JsonResponse(
        {"user": user, "token": token, "error": None}, status=HTTP_200_OK
    )


@api_view(["GET"])
@permission_classes((AllowAny,))
def send_email(request):
    subject = "test"
    body = """
    Hola, este es un mensaje de prueba
    """
    users = User.objects.all()
    send_email_job(users, subject, body)
    return JsonResponse({"user": str(request.user)}, status=HTTP_200_OK)
