from rest_framework import serializers
from .models import ChatTurn
from django.contrib.auth.models import User
# serializers.py
from rest_framework import serializers
from rest_framework.serializers import Serializer, CharField

class ChatTurnSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatTurn
        fields = ["id", "text_user", "text_ai", "created_at"]
        read_only_fields = ["id", "created_at"]

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    
class ResetPasswordSerializer(Serializer):
    email = CharField(required=True)
    confirmation_code = CharField(required=True)
    new_password = CharField(required=True)
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username']

       