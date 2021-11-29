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
    ChangeOPRequestMessage,
    StatusLog,
    ChangeOPRequestFile,
    ChangeOPRequestMessageFile,
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


class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"


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


class OperationProgramSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OperationProgram
        fields = "__all__"
        ordering = ["-start_at"]

    op_type = OperationProgramTypeSerializer


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


class ContractTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ContractType
        fields = "__all__"


class ChangeOPRequestStatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPRequestStatus
        fields = "__all__"

    contract_type = ContractTypeSerializer(many=False, read_only=True)


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


class ChangeOPRequestMessageFileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPRequestMessageFile
        fields = "__all__"
        ordering = ["-file"]


class CreateChangeOPRequestMessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPRequestMessage
        fields = "__all__"
        ordering = ["-created_at"]


class ChangeOPRequestMessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPRequestMessage
        fields = (
            "url",
            "created_at",
            "message",
            "creator",
            "change_op_request",
            "change_op_request_message_files",
        )
        ordering = ["-created_at"]

    change_op_request_message_files = ChangeOPRequestMessageFileSerializer(
        many=True, read_only=True
    )
    creator = BasicUserSerializer(many=False, read_only=True)


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
    change_op_request = ChangeOPRequestSerializer


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


class ChangeOPRequestFileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPRequestFile
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
            "message",
            "updated_at",
            "reason",
            "op_release_date",
            "change_op_request_messages",
            "change_op_request_files",
            "op_change_logs",
            "status_logs",
        )
        ordering = ["-start_at"]
        depth = 2

    reason = ChoiceField(ChangeOPRequest.REASON_CHOICES)
    creator = BasicUserSerializer(many=False, read_only=True)
    op = OperationProgramSerializer(many=False, read_only=True)
    status = ChangeOPRequestStatusSerializer(many=False, read_only=True)
    counterpart = OrganizationSerializer(many=False, read_only=True)
    contract_type = ContractTypeSerializer(many=False, read_only=True)
    change_op_request_messages = ChangeOPRequestMessageSerializer(
        many=True, read_only=True
    )
    op_change_logs = OPChangeLogSerializer(many=True, read_only=True)
    status_logs = StatusLogSerializer(many=True, read_only=True)
    change_op_request_files = ChangeOPRequestFileSerializer(many=True, read_only=True)
