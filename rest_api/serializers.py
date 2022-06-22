from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers

from rest_api.models import User as ApiUser, OperationProgram, OperationProgramType, Organization, ContractType, \
    ChangeOPRequest, ChangeOPRequestStatus, OPChangeLog, OperationProgramStatus, \
    ChangeOPProcessMessageFile, ChangeOPProcessMessage, ChangeOPProcessFile, ChangeOPProcess, ChangeOPProcessStatus, \
    ChangeOPProcessLog, ChangeOPRequestLog


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
        fields = ["url", "email", "first_name", "last_name", "organization", "role", "access_to_ops", "access_to_users",
                  "access_to_organizations"]

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


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    def validate(self, data):
        """
        Check that new_password1 and new_password2 are equal
        """
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError("La nueva contraseña no coincide")

        return data

    def validate_new_password1(self, value):
        validate_password(value)
        return value

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Your old password was entered incorrectly. Please enter it again.')
        return value

    def save(self, **kwargs):
        password = self.validated_data['new_password1']
        user = self.context['request'].user
        user.set_password(password)
        user.save()

        return user


class OperationProgramTypeSerializer(serializers.HyperlinkedModelSerializer):
    ordering = ["-name"]

    class Meta:
        model = OperationProgramType
        fields = "__all__"


class OPChangeLogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OPChangeLog
        fields = "__all__"

    user = UserSerializer(many=False, read_only=True)


class OperationProgramSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OperationProgram
        fields = ("url", "start_at", "op_type", "op_change_logs")
        ordering = ["-start_at"]

    op_type = OperationProgramTypeSerializer(many=False, read_only=True)
    op_change_logs = OPChangeLogSerializer(many=True, read_only=True)


class OperationProgramCreateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OperationProgram
        fields = ("start_at", "op_type")


class BasicUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["url", "email", "first_name", "last_name", "organization", "role"]

    organization = OrganizationSerializer(many=False, read_only=True)


class ChangeOPRequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPRequest
        fields = ["created_at", "creator", "contract_type", "counterpart", "operation_program", "reason",
                  "related_requests", "status", "status_logs", "title", "updated_at", "url"]
        depth = 1
        ordering = ["-start_at"]

    reason = ChoiceField(ChangeOPRequest.REASON_CHOICES)
    creator = UserSerializer(many=False, read_only=True)
    op = OperationProgramSerializer(many=False, read_only=True)
    status = ChangeOPRequestStatusSerializer(many=False, read_only=True)
    counterpart = OrganizationSerializer(many=False, read_only=True)
    contract_type = ContractTypeSerializer(many=False, read_only=True)


class ChangeOPRequestLogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPRequestLog
        fields = "__all__"
        ordering = ["id"]

    user = BasicUserSerializer(many=False, read_only=True)
    change_op_request = ChangeOPRequestSerializer(many=False, read_only=True)


class ChangeOPRequestCreateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPRequest
        fields = "__all__"

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
        fields = ["url", "created_at", "message", "creator", "change_op_process", "change_op_process_message_files"]
        ordering = ["-created_at"]

    change_op_process_message_files = ChangeOPProcessMessageFileSerializer(many=True, read_only=True)
    creator = BasicUserSerializer(many=False, read_only=True)


class ChangeOPRequestDetailMiniSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPRequest
        fields = ["url", "operation_program", "title", "reason"]


class OperationProgramDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OperationProgram
        fields = ("url", "start_at", "op_type", "op_change_logs")
        ordering = ["-start_at"]
        depth = 1

    op_type = OperationProgramTypeSerializer(many=False, read_only=True)
    op_change_logs = OPChangeLogSerializer(many=True, read_only=True)


class ChangeOPProcessStatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPProcessStatus
        fields = "__all__"

    contract_type = ContractTypeSerializer(many=False, read_only=True)


class ChangeOPProcessLogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPProcessLog
        fields = ("url", "created_at", "user", "type", "previous_data", "new_data", "change_op_process",)
        ordering = ["-created_at"]

    user = BasicUserSerializer(many=False, read_only=True)


class ChangeOPProcessFileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPProcessFile
        fields = "__all__"
        ordering = ["-file"]


class ChangeOPRequestDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPRequest
        fields = ["url", "title", "created_at", "creator", "operation_program", "status", "reason", "related_requests",
                  "related_routes", "change_op_requests_logs"]
        ordering = ["-start_at"]
        depth = 2

    creator = BasicUserSerializer(many=False, read_only=True)
    operation_program = OperationProgramSerializer(many=False, read_only=True)
    status = ChangeOPRequestStatusSerializer(many=False, read_only=True)
    reason = ChoiceField(ChangeOPRequest.REASON_CHOICES)
    related_requests = ChangeOPRequestDetailMiniSerializer(many=True)
    change_op_requests_logs = ChangeOPRequestLogSerializer(many=True, read_only=True)


class OperationProgramStatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OperationProgramStatus
        fields = "__all__"
        ordering = ["-name"]

    contract_type = ContractTypeSerializer(many=False, read_only=True)


class ChangeOPProcessSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPProcess
        fields = ["url", "title", "message", "created_at", "updated_at", "counterpart", "contract_type", "creator",
                  "status", "op_release_date", "change_op_requests_count",
                  "operation_program"]
        depth = 1
        ordering = ["created_at"]

    creator = UserSerializer(many=False, read_only=True)
    status = ChangeOPProcessStatusSerializer(many=False, read_only=True)
    counterpart = OrganizationSerializer(many=False, read_only=True)
    contract_type = ContractTypeSerializer(many=False, read_only=True)

    operation_program = OperationProgramSerializer(many=False, read_only=True)
    change_op_requests_count = serializers.IntegerField()


class ChangeOPProcessDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPProcess
        fields = ["url", "title", "message", "created_at", "updated_at", "counterpart", "contract_type",
                  "operation_program", "creator", "status", "op_release_date",
                  "change_op_requests", "change_op_process_messages", "change_op_process_files",
                  "change_op_process_logs"]
        ordering = ["-start_at"]
        depth = 2

    counterpart = OrganizationSerializer(many=False, read_only=True)
    contract_type = ContractTypeSerializer(many=False, read_only=True)
    operation_program = OperationProgramSerializer(many=False, read_only=True)
    creator = BasicUserSerializer(many=False, read_only=True)
    status = ChangeOPRequestStatusSerializer(many=False, read_only=True)

    change_op_requests = ChangeOPRequestDetailSerializer(many=True)
    change_op_process_messages = ChangeOPProcessMessageSerializer(many=True, read_only=True)
    change_op_process_files = ChangeOPProcessFileSerializer(many=True, read_only=True)
    change_op_process_logs = ChangeOPProcessLogSerializer(many=True, read_only=True)


class ChangeOPProcessCreateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChangeOPProcess
        fields = ['title', 'message', 'counterpart', 'operation_program']

    counterpart = OrganizationSerializer

    def save(self, **kwargs):
        user = self.context['request'].user
        organization = user.organization
        contract_type = organization.contract_type

        data = self.validated_data
        data['created_at'] = timezone.now()
        data['updated_at'] = timezone.now()
        data['creator'] = user

        if contract_type.pk == ContractType.BOTH:
            data['contract_type'] = data['counterpart'].contract_type
        else:
            data['contract_type'] = contract_type

        status_obj = ChangeOPProcessStatus.objects.get(contract_type=data['contract_type'],
                                                       name="Evaluando admisibilidad")
        data["status"] = status_obj
        if 'operation_program' in data and data['operation_program'] is not None:
            data['op_release_date'] = data['operation_program'].start_at

        change_op_process_obj = ChangeOPProcess.objects.create(**data)

        errors = []
        try:
            files = self.context['request'].FILES.getlist("files")
            for file in files:
                ChangeOPProcessFile.objects.create(file=file, change_op_process_id=change_op_process_obj.pk)
        except Exception as e:
            errors.append(e)

        return change_op_process_obj
