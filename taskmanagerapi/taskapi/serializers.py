from rest_framework import serializers
from taskapi.models import User
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from taskapi import utils
from .models import Task



# User Serializer

class UserRegistrationSerializer(serializers.ModelSerializer):
    # we are writting about this field bcoz we required this in the registration page
    password2 = serializers.CharField(style={'input_type' : 'password'}, write_only=True)
    class Meta: 
        model = User
        fields = ['name', 'email', 'password', 'password2']
        extra_kwargs={
            'password':{'write_only' : True}
        }


    # validating password and comfirm password while registering the user
    def validate(self, attrs):
        password = attrs.get('password')
        passwor2 = attrs.get('password2')
        if password != passwor2:
            raise serializers.ValidationError("password and confirm passwrd doesn't match")
        return attrs
    

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = User
        fields= ['email', 'password']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']


class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type' : 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type' : 'passwor2'}, write_only=True)
    class Meta:
        model = User
        fields=['password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')
        if password != password2:
            raise serializers.ValidationError("password and confirm passwrd doesn't match")
        user.set_password(password)
        user.save()
        return attrs
    

class SendPasswordResetEmailSerializer(serializers.Serializer):
        email = serializers.EmailField(max_length=255)
        class Meta:
            fields=['email']

        def validate(self, attrs):
            email = attrs.get('email')
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                uid = urlsafe_base64_encode(force_bytes(user.id))
                print("Encoded URI" , uid)
                token = PasswordResetTokenGenerator().make_token(user)
                print('password reset token', token)
                link='http://127.0.0.1:8000/auth/api/reset/'+uid+'/'+token
                print('password reset link', link)
                body = 'Click the following to reset the password' + link
                data={
                    'subject' : 'Reset password link',
                    'body':body,
                    'to_email' : user.email
                    
                }
                utils.send_email(data)
                return attrs
            else:
                return ValueError('You are not registered user.')


class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type' : 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type' : 'passwor2'}, write_only=True)
    class Meta:
        model = User
        fields=['password', 'password2']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')
            if password != password2:
                raise serializers.ValidationError("password and confirm passwrd doesn't match")
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise ValueError('Token is not valid or Expired.')
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise ValueError('Token is not valid or Expired.')
    

# Task Serilizer

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ("id", "user", "created_at", "updated_at")






        