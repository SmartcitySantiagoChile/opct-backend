import os.path

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from nested_inline.admin import NestedStackedInline, NestedModelAdmin

from rest_api import models
from rest_api.models import RouteDictionary


@admin.register(models.User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    exclude = ["groups", "user_permissions"]
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
                    "access_to_upload_route_dictionary",
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

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # after save update permission groups
        op_group_obj = Group.objects.get(name="Operation Program")
        org_group_obj = Group.objects.get(name="Organization")
        user_group_obj = Group.objects.get(name="User")
        upload_route_dict_group_obj = Group.objects.get(name="Upload Route Dictionary")
        if obj.access_to_ops:
            op_group_obj.user_set.add(obj)
        else:
            op_group_obj.user_set.remove(obj)

        if obj.access_to_organizations:
            org_group_obj.user_set.add(obj)
        else:
            org_group_obj.user_set.remove(obj)

        if obj.access_to_users:
            user_group_obj.user_set.add(obj)
        else:
            user_group_obj.user_set.remove(obj)

        if obj.access_to_upload_route_dictionary:
            upload_route_dict_group_obj.user_set.add(obj)
        else:
            upload_route_dict_group_obj.user_set.remove(obj)


class RouteDictionaryAdmin(admin.ModelAdmin):
    actions = None
    search_fields = ['ts_code', 'user_route_code', 'service_name', 'operator']
    list_display = ('ts_code', 'user_route_code', 'service_name', 'operator', 'updated_at', 'created_at')
    change_list_template = os.path.join('rest_api', 'routedictionary', 'change_list.html')


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
