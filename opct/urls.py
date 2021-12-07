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
from rest_api import views
from rest_api.views import login, verify, send_email, change_op_request_reasons

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"operation-programs", views.OperationProgramViewSet)
router.register(r"operation-program-types", views.OperationProgramTypeViewSet)
router.register(r"organizations", views.OrganizationViewSet)
router.register(r"contract-types", views.ContractTypeViewSet)
router.register(r"change-op-requests", views.ChangeOPRequestViewSet),
router.register(r"change-op-request-statuses", views.ChangeOPRequestStatusViewSet)
router.register(r"change-op-data-logs", views.OPChangeDataLogViewset)
router.register(r"change-op-request-messages", views.ChangeOPRequestMessageViewSet)
router.register(r"op-change-logs", views.OPChangeLogViewSet)
router.register(r"status-logs", views.StatusLogViewSet)
router.register(r"change-op-request-files", views.ChangeOPRequestFileViewset)
router.register(
    r"change-op-request-message-files", views.ChangeOPRequestMessageFileViewset
)
router.register(r"operation-program-statuses", views.OperationProgramStatusViewSet)

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
