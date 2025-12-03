from rest_framework import serializers
from .models import ChatTurn, Itinerary,Destination
from rest_framework import serializers
from rest_framework.serializers import Serializer, CharField
from django.contrib.auth.models import User

from .models import ChatTurn, Itinerary
#serializers.py
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


class ItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerary
        fields = ['id', 'user', 'title', 'details', 'is_fixed', 'is_public', 'created_at']
    
class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ['id', 'name', 'description', 'location', 'latitude', 'longitude', 'image_url', 'created_at']
        read_only_fields = ['id', 'created_at']
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username']

       
class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login']
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']