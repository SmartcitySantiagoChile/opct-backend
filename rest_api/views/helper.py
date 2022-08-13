from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_409_CONFLICT, HTTP_204_NO_CONTENT

from rest_api.exceptions import CustomValidation
from rest_api.models import User, Organization, ContractType, ChangeOPRequest
from rest_api.permissions import HasGroupPermission
from rest_api.serializers import UserSerializer, UserLoginSerializer, UserTokenSerializer, OrganizationSerializer, \
    ContractTypeSerializer, OrganizationCreateSerializer, ChangePasswordSerializer


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


class ChangePasswordAPIView(UpdateAPIView):
    """
    API endpoint to change user password
    """
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=HTTP_204_NO_CONTENT)


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Organizations to be viewed, created, updated and delete.
    Only can delete if it does not exist a related User.
    """
    queryset = Organization.objects.all().order_by("-name")
    permission_classes = [IsAuthenticated, HasGroupPermission]
    pagination_class = None

    required_groups = {
        "GET": [],
        "POST": ["Organization"],
        "PUT": ["Organization"],
        "DELETE": ["Organization"],
    }

    def get_serializer_class(self):
        if self.action == 'create':
            return OrganizationCreateSerializer
        return OrganizationSerializer

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


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
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
