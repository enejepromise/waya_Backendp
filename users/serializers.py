from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from allauth.account import app_settings
from users.models import EmailVerification

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=app_settings.SIGNUP_FIELDS['email']['required'])
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, label='Confirm password', style={'input_type': 'password'})
    terms_accepted = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'password', 'password2', 'role', 'terms_accepted', 'avatar']
        extra_kwargs = {
            'role': {'default': User.ROLE_PARENT},
            'avatar': {'required': False, 'allow_null': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("A user with this email already exists."))
        return value

    def validate_terms_accepted(self, value):
        if not value:
            raise serializers.ValidationError(_("You must accept the Terms and Conditions."))
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({"password": _("Password fields didn't match.")})

        try:
            validate_password(attrs.get('password'))
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        token = EmailVerification.objects.create(user=user)

        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value):
        user = self.context['request'].user
        try:
            validate_password(value, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs.get('old_password')):
            raise serializers.ValidationError({"old_password": _("Old password is not correct.")})
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("User with this email does not exist."))
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(write_only=True, required=True)
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs.get('new_password1') != attrs.get('new_password2'):
            raise serializers.ValidationError({"new_password2": _("Password fields didn't match.")})

        user = self.context.get('user')
        try:
            validate_password(attrs.get('new_password1'), user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"new_password1": list(e.messages)})

        return attrs

    def save(self, **kwargs):
        user = self.context.get('user')
        user.set_password(self.validated_data['new_password1'])
        user.save()
        return user


class EmailVerificationSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
