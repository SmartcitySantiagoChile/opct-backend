from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from nested_inline.admin import NestedStackedInline, NestedModelAdmin

from rest_api import models
from rest_api.models import RouteDictionary


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


class RouteDictionaryAdmin(admin.ModelAdmin):
    actions = None
    search_fields = ['auth_route_code', 'user_route_code', 'op_route_code', 'route_type']
    list_display = ('auth_route_code', 'user_route_code', 'op_route_code', 'route_type', 'created_at', 'operator')


class OperationProgramStatusAdmin(admin.ModelAdmin):
    list_display = ("name", "contract_type")


class CounterPartContactInLine(admin.TabularInline):
    model = models.CounterPartContact
    fk_name = "organization"


class OrganizationAdmin(admin.ModelAdmin):
    inlines = [CounterPartContactInLine]


class ChangeOPProcessMessageFile(NestedStackedInline):
    model = models.ChangeOPProcessMessageFile
    fk_name = "change_op_process_message"


class ChangeOPProcessMessage(NestedStackedInline):
    model = models.ChangeOPProcessMessage
    fk_name = "change_op_process"
    inlines = [ChangeOPProcessMessageFile]


class OPChangeLog(NestedStackedInline):
    model = models.OPChangeLog
    fk_name = "change_op_process"


class ChangeOPProcessMessageAdmin(admin.ModelAdmin):
    inlines = [ChangeOPProcessMessageFile]


class ChangeOpProcessAdmin(NestedModelAdmin):
    save_as = True
    inlines = [ChangeOPProcessMessage]


class OPChangeLogAdmin(admin.ModelAdmin):
    model = models.OPChangeLog


class ChangeOpRequestAdmin(admin.ModelAdmin):
    model = models.ChangeOPRequest


class ChangeOPProcessLogAdmin(admin.ModelAdmin):
    model = models.ChangeOPProcessLog


class ChangeOPRequestLogAdmin(admin.ModelAdmin):
    model = models.ChangeOPRequestLog


admin.site.register(models.ChangeOPProcess, ChangeOpProcessAdmin)
admin.site.register(models.ChangeOPRequest, ChangeOpRequestAdmin)
admin.site.register(models.ChangeOPProcessMessage, ChangeOPProcessMessageAdmin)
admin.site.register(models.ContractType)
admin.site.register(models.OPChangeLog, OPChangeLogAdmin)
admin.site.register(models.OperationProgram)
admin.site.register(models.OperationProgramStatus, OperationProgramStatusAdmin)
admin.site.register(models.OperationProgramType)
admin.site.register(models.Organization, OrganizationAdmin)
admin.site.register(models.ChangeOPProcessLog, ChangeOPProcessLogAdmin)
admin.site.register(models.ChangeOPRequestLog, ChangeOPRequestLogAdmin)
admin.site.register(RouteDictionary, RouteDictionaryAdmin)
