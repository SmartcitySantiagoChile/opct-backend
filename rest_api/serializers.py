from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers

from rest_api.models import (
    User as ApiUser,
    OperationProgram,
    OperationProgramType,
    Organization,
    ContractType,
    ChangeOPRequest,
    ChangeOPRequestStatus,
    OPChangeDataLog,
    OPChangeLog,
    StatusLog,
    OperationProgramStatus,
    ChangeOPProcessMessageFile,
    ChangeOPProcessMessage,
    ChangeOPProcessFile,
    ChangeOPProcess,
    ChangeOPProcessStatus,
    ChangeOPProcessStatusLog,
)


class ChoiceField(serializers.ChoiceField):
    def to_representation(self, obj):
        if obj == "" and self.allow_blank:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        # To support inserts with the value
        if data == "" and self.allow_blank:
            return ""

        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail("invalid_choice", input=data)


class ContractTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ContractType
        fields = "__all__"


class ChangeOPRequestStatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPRequestStatus
        fields = "__all__"

    contract_type = ContractTypeSerializer(many=False, read_only=True)


class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
        fields = ("url", "name", "created_at", "contract_type", "default_counterpart")

    contract_type = ContractTypeSerializer(many=False, read_only=True)


class OrganizationCreateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
        fields = ("name", "created_at", "contract_type", "default_counterpart")


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "url",
            "email",
            "first_name",
            "last_name",
            "organization",
            "role",
            "access_to_ops",
            "access_to_users",
            "access_to_organizations",
        ]

    organization = OrganizationSerializer(many=False, read_only=True)


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, max_length=64)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError()
        self.context["user"] = user
        return data


class UserTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField(min_length=12)

    def validate(self, data):
        email = data.get("email")
        user = ApiUser.objects.get(email=email)
        if not user:
            raise serializers.ValidationError()
        self.context["user"] = user
        return data


class OperationProgramTypeSerializer(serializers.HyperlinkedModelSerializer):
    ordering = ["-name"]

    class Meta:
        model = OperationProgramType
        fields = "__all__"


class OPChangeDataLogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OPChangeDataLog
        fields = "__all__"

    user = UserSerializer(many=False, read_only=True)


class OperationProgramSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OperationProgram
        fields = ("url", "start_at", "op_type", "op_change_data_logs")
        ordering = ["-start_at"]
        depth = 1

    op_type = OperationProgramTypeSerializer(many=False, read_only=True)
    op_change_data_logs = OPChangeDataLogSerializer(many=True, read_only=True)


class OperationProgramCreateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OperationProgram
        fields = ("start_at", "op_type")


class BasicUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "url",
            "email",
            "first_name",
            "last_name",
            "organization",
            "role",
        ]

    organization = OrganizationSerializer(many=False, read_only=True)


class OPChangeDataLogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OPChangeDataLog
        fields = "__all__"


class ChangeOPRequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPRequest
        fields = "__all__"
        depth = 1
        ordering = ["-start_at"]

    reason = ChoiceField(ChangeOPRequest.REASON_CHOICES)
    creator = UserSerializer(many=False, read_only=True)
    op = OperationProgramSerializer(many=False, read_only=True)
    status = ChangeOPRequestStatusSerializer(many=False, read_only=True)
    counterpart = OrganizationSerializer(many=False, read_only=True)
    contract_type = ContractTypeSerializer(many=False, read_only=True)


class ChangeOPRequestCreateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPRequest
        fields = "__all__"

    reason = ChoiceField(ChangeOPRequest.REASON_CHOICES)
    creator = UserSerializer
    status = ChangeOPRequestStatusSerializer
    counterpart = OrganizationSerializer


class ChangeOPProcessMessageFileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPProcessMessageFile
        fields = "__all__"
        ordering = ["-file"]


class CreateChangeOPProcessMessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPProcessMessage
        fields = "__all__"
        ordering = ["-created_at"]


class ChangeOPProcessMessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPProcessMessage
        fields = (
            "url",
            "created_at",
            "message",
            "creator",
            "change_op_process",
            "change_op_process_message_files",
        )
        ordering = ["-created_at"]

    change_op_process_message_files = ChangeOPProcessMessageFileSerializer(
        many=True, read_only=True
    )
    creator = BasicUserSerializer(many=False, read_only=True)


class ChangeOPRequestDetailMiniSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPRequest
        fields = ["url", "op", "title", "reason"]


class OperationProgramDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OperationProgram
        fields = ("url", "start_at", "op_type", "op_change_data_logs")
        ordering = ["-start_at"]
        depth = 1

    op_type = OperationProgramTypeSerializer
    op_change_data_logs = OPChangeDataLogSerializer


class OPChangeLogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OPChangeLog
        fields = "__all__"

    creator = BasicUserSerializer(many=False, read_only=True)
    previous_op = OperationProgramSerializer(many=False, read_only=True)
    new_op = OperationProgramSerializer(many=False, read_only=True)
    change_op_request = ChangeOPRequestSerializer(many=False, read_only=True)


class StatusLogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = StatusLog
        fields = (
            "url",
            "created_at",
            "user",
            "previous_status",
            "new_status",
            "change_op_request",
        )
        ordering = ["-created_at"]

    user = BasicUserSerializer(many=False, read_only=True)
    previous_status = ChangeOPRequestStatusSerializer(many=False, read_only=True)
    new_status = ChangeOPRequestStatusSerializer(many=False, read_only=True)
    change_op_request = ChangeOPRequestSerializer(many=False, read_only=True)


class ChangeOPProcessStatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPProcessStatus
        fields = "__all__"

    contract_type = ContractTypeSerializer(many=False, read_only=True)


class ChangeOPProcessStatusLogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPProcessStatusLog
        fields = (
            "url",
            "created_at",
            "user",
            "previous_status",
            "new_status",
            "change_op_process",
        )
        ordering = ["-created_at"]

    user = BasicUserSerializer(many=False, read_only=True)
    previous_status = ChangeOPProcessStatusSerializer(many=False, read_only=True)
    new_status = ChangeOPRequestStatusSerializer(many=False, read_only=True)


class ChangeOPProcessFileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPProcessFile
        fields = "__all__"
        ordering = ["-file"]


class ChangeOPRequestDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPRequest
        fields = (
            "url",
            "creator",
            "op",
            "status",
            "counterpart",
            "contract_type",
            "created_at",
            "title",
            "updated_at",
            "reason",
            "op_release_date",
            "op_change_logs",
            "status_logs",
            "related_requests",
        )
        ordering = ["-start_at"]
        depth = 2

    reason = ChoiceField(ChangeOPRequest.REASON_CHOICES)
    creator = BasicUserSerializer(many=False, read_only=True)
    op = OperationProgramSerializer(many=False, read_only=True)
    status = ChangeOPRequestStatusSerializer(many=False, read_only=True)
    counterpart = OrganizationSerializer(many=False, read_only=True)
    contract_type = ContractTypeSerializer(many=False, read_only=True)
    op_change_logs = OPChangeLogSerializer(many=True, read_only=True)
    status_logs = StatusLogSerializer(many=True, read_only=True)
    related_requests = ChangeOPRequestDetailMiniSerializer(many=True)


class OperationProgramStatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OperationProgramStatus
        fields = "__all__"
        ordering = ["-name"]

    contract_type = ContractTypeSerializer(many=False, read_only=True)


class ChangeOPProcessStatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPProcessStatus
        fields = "__all__"

    contract_type = ContractTypeSerializer(many=False, read_only=True)


class ChangeOPProcessSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPProcess
        fields = "__all__"
        depth = 1
        ordering = ["-created_at"]

    creator = UserSerializer(many=False, read_only=True)
    base_op = OperationProgramSerializer(many=False, read_only=True)
    status = ChangeOPProcessStatusSerializer(many=False, read_only=True)
    counterpart = OrganizationSerializer(many=False, read_only=True)
    contract_type = ContractTypeSerializer(many=False, read_only=True)


class ChangeOPProcessDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPProcess
        fields = (
            "url",
            "creator",
            "base_op",
            "status",
            "counterpart",
            "contract_type",
            "title",
            "message",
            "created_at",
            "updated_at",
            "change_op_requests",
            "change_op_process_messages",
            "change_op_process_files",
            "change_op_process_status_logs",
            "op_change_logs",
        )
        ordering = ["-start_at"]
        depth = 2

    creator = BasicUserSerializer(many=False, read_only=True)
    base_op = OperationProgramSerializer(many=False, read_only=True)
    status = ChangeOPRequestStatusSerializer(many=False, read_only=True)
    counterpart = OrganizationSerializer(many=False, read_only=True)
    contract_type = ContractTypeSerializer(many=False, read_only=True)
    change_op_requests = ChangeOPRequestDetailSerializer(many=True)
    change_op_process_messages = ChangeOPProcessMessageSerializer(
        many=True, read_only=True
    )
    change_op_process_files = ChangeOPProcessFileSerializer(many=True, read_only=True)
    change_op_process_status_logs = ChangeOPProcessStatusLogSerializer(
        many=True, read_only=True
    )
    op_change_logs = OPChangeLogSerializer(many=True, read_only=True)
