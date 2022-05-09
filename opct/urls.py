"""opct URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from rest_framework import routers

from opct import settings
from rest_api.views.change_op_process import (
    ChangeOPProcessMessageViewSet,
    OPChangeLogViewSet,
    ChangeOPProcessStatusLogViewSet,
    ChangeOPProcessFileViewset,
    ChangeOPProcessMessageFileViewset,
    ChangeOPProcessViewSet,
    ChangeOPProcessStatusViewSet,
)
from rest_api.views.change_op_request import (
    ChangeOPRequestViewSet,
    ChangeOPRequestStatusViewSet,
    StatusLogViewSet,
)
from rest_api.views.helper import (
    login,
    verify,
    send_email,
    change_op_request_reasons,
    UserViewSet,
    OrganizationViewSet,
    ContractTypeViewSet,
    ChangeOPRequestOPChangeLogViewSet,
    ChangeOPRequestReasonChangeLogViewSet,
)
from rest_api.views.operation_program import (
    OperationProgramViewSet,
    OperationProgramTypeViewSet,
    OPChangeDataLogViewset,
    OperationProgramStatusViewSet,
    OPChangeDataLogViewSet,
)

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"operation-programs", OperationProgramViewSet)
router.register(r"operation-program-types", OperationProgramTypeViewSet)
router.register(r"organizations", OrganizationViewSet)
router.register(r"contract-types", ContractTypeViewSet)
router.register(r"change-op-requests", ChangeOPRequestViewSet),
router.register(r"change-op-request-statuses", ChangeOPRequestStatusViewSet)
router.register(r"change-op-data-logs", OPChangeDataLogViewset)
router.register(r"change-op-process-messages", ChangeOPProcessMessageViewSet)
router.register(r"op-change-logs", OPChangeLogViewSet)
router.register(r"status-logs", StatusLogViewSet)
router.register(r"change-op-process-status-logs", ChangeOPProcessStatusLogViewSet)
router.register(r"change-op-process-files", ChangeOPProcessFileViewset)
router.register(r"change-op-process-message-files", ChangeOPProcessMessageFileViewset)
router.register(r"operation-program-statuses", OperationProgramStatusViewSet)
router.register(r"op-change-data-logs", OPChangeDataLogViewSet)
router.register(r"change-op-processes", ChangeOPProcessViewSet)
router.register(r"change-op-process-statuses", ChangeOPProcessStatusViewSet)
router.register(r"change-op-request-op-change-log", ChangeOPRequestOPChangeLogViewSet)
router.register(
    r"change-op-request-reason-change-log", ChangeOPRequestReasonChangeLogViewSet
)

urlpatterns = [
    path("", RedirectView.as_view(url="/api/")),
    path("admin/", admin.site.urls),
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api/", include(router.urls)),
    path("api/login", login, name="login"),
    path("api/verify/", verify, name="verify"),
    path("api/send-mail/", send_email, name="send-email"),
    path(
        "api/change-op-request-reasons/",
        change_op_request_reasons,
        name="change-op-request-reasons",
    ),
]

if settings.DEBUG:
    # it serves media files in dev server
    from django.conf.urls.static import static

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
