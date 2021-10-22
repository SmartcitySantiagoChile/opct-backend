from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.status import (HTTP_200_OK)

from rest_api.models import User, OperationProgram, OperationProgramType, Organization, ContractType
from rest_api.permissions import HasGroupPermission
from rest_api.serializers import UserSerializer, GroupSerializer, UserLoginSerializer, UserTokenSerializer, \
    OperationProgramSerializer, OperationProgramTypeSerializer, OrganizationSerializer, ContractTypeSerializer
from rqworkers.tasks import send_email_job


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [HasGroupPermission]
    required_groups = {'GET': ['User Editor'],
                       'POST': ['User Editor'],
                       'PUT': ['User Editor'],
                       'DELETE': ['User Editor']}


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]


class OperationProgramViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Operation Programs to be viewed or edited.
    """
    queryset = OperationProgram.objects.all()
    serializer_class = OperationProgramSerializer
    permission_classes = [HasGroupPermission]
    required_groups = {'GET': ['Operation Program Editor'],
                       'POST': ['Operation Program Editor'],
                       'PUT': ['Operation Program Editor'],
                       'DELETE': ['Operation Program Editor']}


class OperationProgramTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Operation Programs Type to be viewed or edited.
    """
    queryset = OperationProgramType.objects.all()
    serializer_class = OperationProgramTypeSerializer
    permission_classes = [HasGroupPermission, IsAdminUser]

    required_groups = {'GET': ['Operation Program Editor'],
                       'POST': ['Operation Program Editor'],
                       'PUT': ['Operation Program Editor'],
                       'DELETE': ['Operation Program Editor']}


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Organizations  to be viewed or edited.
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [HasGroupPermission]

    required_groups = {'GET': ['Organization Editor'],
                       'POST': ['Organization Editor'],
                       'PUT': ['Organization Editor'],
                       'DELETE': ['Organization Editor']}

class ContractTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Contract Type to be viewed or edited.
    """
    queryset = ContractType.objects.all()
    serializer_class = ContractTypeSerializer
    permission_classes = [IsAdminUser]


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    login_serializer = UserLoginSerializer(data=request.data)
    data = login_serializer.is_valid()
    if not data:
        raise AuthenticationFailed()
    user = login_serializer.context['user']
    token, _ = Token.objects.get_or_create(user=login_serializer.context['user'])
    return JsonResponse({'user': str(user),
                         'token': token.key,
                         'error': None},
                        status=HTTP_200_OK)


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def verify(request):
    user = str(request.user)
    token = str(request.auth)
    data = {'email': user, 'token': token}
    token_serializer = UserTokenSerializer(data=data)
    data = token_serializer.is_valid()
    if not data:
        raise AuthenticationFailed()
    return JsonResponse({'user': user,
                         'token': token,
                         'error': None}, status=HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
def send_email(request):
    subject = "test"
    body = """
    Hola, este es un mensaje de prueba
    """
    users = User.objects.all()
    send_email_job(users, subject, body)
    return JsonResponse({'user': str(request.user)}, status=HTTP_200_OK)
