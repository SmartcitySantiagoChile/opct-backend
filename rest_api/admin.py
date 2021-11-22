from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _
from rest_api import models
from nested_inline.admin import NestedStackedInline, NestedModelAdmin


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


class CounterPartContactInLine(admin.TabularInline):
    model = models.CounterPartContact
    fk_name = "organization"


class OrganizationAdmin(admin.ModelAdmin):
    inlines = [CounterPartContactInLine]


class ChangeOPRequestMessageFile(NestedStackedInline):
    model = models.ChangeOPRequestMessageFile
    fk_name = "change_op_request_message"


class ChangeOPRequestMessage(NestedStackedInline):
    model = models.ChangeOPRequestMessage
    fk_name = "change_op_request"
    inlines = [ChangeOPRequestMessageFile]


class ChangeOPRequestFile(NestedStackedInline):
    model = models.ChangeOPRequestFile
    fk_name = "change_op_request"


class StatusLog(NestedStackedInline):
    model = models.StatusLog
    fk_name = "change_op_request"


class OPChangeLog(NestedStackedInline):
    model = models.OPChangeLog
    fk_name = "change_op_request"


class ChangeOPRequestMessageAdmin(admin.ModelAdmin):
    inlines = [ChangeOPRequestMessageFile]


class ChangeOpRequestAdmin(NestedModelAdmin):
    save_as = True
    inlines = [ChangeOPRequestFile, ChangeOPRequestMessage, StatusLog, OPChangeLog]


admin.site.register(models.ChangeOPRequest, ChangeOpRequestAdmin)
admin.site.register(models.ChangeOPRequestFile)
admin.site.register(models.ChangeOPRequestMessage, ChangeOPRequestMessageAdmin)
admin.site.register(models.ContractType)
admin.site.register(models.OPChangeLog)
admin.site.register(models.OperationProgram)
admin.site.register(models.OperationProgramStatus, OperationProgramStatusAdmin)
admin.site.register(models.OperationProgramType)
admin.site.register(models.Organization, OrganizationAdmin)
admin.site.register(models.StatusLog)
