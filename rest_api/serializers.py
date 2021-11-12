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
)


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


class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"


class ContractTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ContractType
        fields = "__all__"


class ChangeOPRequestStatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPRequestStatus
        fields = "__all__"


class OPChangeDataLogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OPChangeDataLog
        fields = "__all__"


class ChangeOPRequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPRequest

        fields = "__all__"
        depth = 1

    creator = UserSerializer(many=False, read_only=True)
    op = OperationProgramSerializer(many=False, read_only=True)
    status = ChangeOPRequestStatusSerializer(many=False, read_only=True)
    counterpart = OrganizationSerializer(many=False, read_only=True)
    contract_type = ContractTypeSerializer(many=False, read_only=True)


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

    creator = UserSerializer
    previous_op = OperationProgramSerializer
    new_op = OperationProgramSerializer
    change_op_request = ChangeOPRequestSerializer
