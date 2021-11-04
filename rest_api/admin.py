from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from rest_api import models


@admin.register(models.User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Datos de sistema"),
            {
                "fields": (
                    "organization",
                    "access_to_ops",
                    "access_to_organizations",
                    "access_to_users",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_display = ("email", "first_name", "last_name", "is_staff", "organization")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


class OperationProgramStatusAdmin(admin.ModelAdmin):
    list_display = ("name", "contract_type")


admin.site.register(models.ChangeOPRequest)
admin.site.register(models.ChangeOPRequestFile)
admin.site.register(models.ChangeOPRequestMessage)
admin.site.register(models.ChangeOPRequestMessageFile)
admin.site.register(models.ContractType)
admin.site.register(models.OPChangeLog)
admin.site.register(models.OperationProgram)
admin.site.register(models.OperationProgramStatus, OperationProgramStatusAdmin)
admin.site.register(models.OperationProgramType)
admin.site.register(models.Organization)
admin.site.register(models.StatusLog)
admin.site.register(models.CounterPartContact)
