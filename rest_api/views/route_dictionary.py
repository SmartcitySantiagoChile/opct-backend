import csv
import gzip
import io
import os
import zipfile

from django.contrib import messages
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from rest_api.models import RouteDictionary
from rest_api.permissions import HasGroupPermission
from rest_api.serializers import RouteDictionarySerializer


def upload_csv_op_dictionary(csv_file: InMemoryUploadedFile) -> dict:
    """
    Upload csv with route dictionary to database
    Args:
        csv_file: csv op dictionary InMemoryUploadedFile
    """
    file_name_extension = os.path.splitext(csv_file.name)[1]
    if file_name_extension == ".gz":
        csv_file = gzip.open(csv_file)
    elif file_name_extension == ".zip":
        zip_file_obj = zipfile.ZipFile(csv_file)
        file_name = zip_file_obj.namelist()[0]
        csv_file = zip_file_obj.open(file_name, 'r')
    csv_file = io.StringIO(csv_file.read().decode('utf-8'))
    upload_time = timezone.now()

    to_create = []
    csv_reader = csv.reader(csv_file, delimiter=";")
    if not csv_reader:
        raise ValueError("Archivo con datos en blanco")
    # skip header
    next(csv_reader)
    for row in csv_reader:
        auth_route_code = str(row[11])
        op_route_code = str(row[9]) + str(row[7])
        user_route_code = row[8]
        route_type = row[1]
        operator = row[3]

        if auth_route_code == '' or op_route_code == '' or user_route_code == '' or route_type == '':
            continue
        to_create.append(RouteDictionary(auth_route_code=auth_route_code,
                                         op_route_code=op_route_code,
                                         user_route_code=user_route_code,
                                         route_type=route_type,
                                         created_at=upload_time,
                                         operator=operator))
    with transaction.atomic():
        RouteDictionary.objects.all().delete()
        RouteDictionary.objects.bulk_create(to_create)

    return {"created": len(to_create)}


class UploadRouteDictionaryFileAPIView(CreateAPIView):
    """
    API endpoint to upload route dictionary file from django admin
    """
    permission_classes = (IsAdminUser,)

    def create(self, request, *args, **kwargs):
        csv_file = request.FILES.get('routeDictionary', False)
        if not csv_file or csv_file.size == 0:
            level = messages.ERROR
            message = "No existe el archivo"
        else:
            try:
                res = upload_csv_op_dictionary(csv_file)
                level = messages.SUCCESS
                message = "{0}".format(res)
            except ValueError as e:
                level = messages.ERROR
                message = str(e)
            except Exception as e:
                level = messages.ERROR
                message = "Archivo en formato incorrecto " + str(e)

        messages.add_message(request, level, message)
        url = reverse('admin:rest_api_routedictionary_changelist')
        return redirect(url)


class RouteDictionaryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows ChangeOPRequestStatus to be viewed.
    """

    queryset = RouteDictionary.objects.all().order_by("auth_route_code")
    serializer_class = RouteDictionarySerializer
    pagination_class = None

    required_groups = {
        "POST": ["Upload Route Dictionary"],
    }

    @action(detail=False, methods=["post"], url_path="update-definitions",
            permission_classes=[HasGroupPermission])
    def update_definitions(self, request, *args, **kwargs):
        csv_file = request.FILES.get('files', None)
        if not csv_file:
            raise ParseError("Archivo no encontrado")
        elif csv_file.size == 0:
            raise ParseError("Archivo no puede ser vacío")
        else:
            try:
                message = upload_csv_op_dictionary(csv_file)
            except ValueError as e:
                message = str(e)
                raise ParseError(message)
            except Exception as e:
                message = "Archivo en formato incorrecto " + str(e)
                raise ParseError(message)

        return Response(message, status=status.HTTP_200_OK)
