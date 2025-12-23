from rest_framework import serializers
from django.contrib.auth.models import User

from .models import (
    ChatTurn,
    Destination,
    Service,
    WeatherInfo,
    Itinerary,
    ItineraryDestination,
    ItineraryReview,
    Airport,
    FlightSegment,
    Preference,
    UserPreference,
)


# =========================
#  CHAT & USER
# =========================
class ChatTurnSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatTurn
        fields = ["id", "text_user", "text_ai", "created_at"]
        read_only_fields = ["id", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id", "username"]


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)


# =========================
#  DESTINATION & RELATED
# =========================
class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = [
            "id",
            "name",
            "short_description",
            "location",
            "latitude",
            "longitude",
            "image_url",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ServiceSerializer(serializers.ModelSerializer):
    destination_id = serializers.PrimaryKeyRelatedField(
        source="destination",
        queryset=Destination.objects.all(),
        write_only=True,
        required=True,
    )
    destination = DestinationSerializer(read_only=True)

    class Meta:
        model = Service
        fields = [
            "id",
            "destination",
            "destination_id",
            "name",
            "service_type",
            "description",
            "address",
            "price_from",
            "price_range",
            "rating_avg",
            "rating_count",
            "image_url",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "destination"]


class WeatherInfoSerializer(serializers.ModelSerializer):
    destination_id = serializers.PrimaryKeyRelatedField(
        source="destination",
        queryset=Destination.objects.all(),
        write_only=True,
        required=True,
    )
    destination = DestinationSerializer(read_only=True)

    class Meta:
        model = WeatherInfo
        fields = [
            "id",
            "destination",
            "destination_id",
            "month",
            "note",
        ]
        read_only_fields = ["id", "destination"]


# =========================
#  ITINERARY
# =========================
class ItineraryDestinationSerializer(serializers.ModelSerializer):
    destination = DestinationSerializer(read_only=True)
    destination_id = serializers.PrimaryKeyRelatedField(
        source="destination",
        queryset=Destination.objects.all(),
        write_only=True,
        required=True,
    )

    class Meta:
        model = ItineraryDestination
        fields = [
            "id",
            "day_number",
            "part_of_day",
            "activity_title",
            "activity_description",
            "order",
            "destination",
            "destination_id",
        ]
        read_only_fields = ["id", "destination"]


class ItinerarySerializer(serializers.ModelSerializer):
    main_destination = DestinationSerializer(read_only=True)
    main_destination_id = serializers.PrimaryKeyRelatedField(
        source="main_destination",
        queryset=Destination.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    base_itinerary = serializers.PrimaryKeyRelatedField(
        queryset=Itinerary.objects.all(),
        required=False,
        allow_null=True,
    )

    destinations_detail = ItineraryDestinationSerializer(
        source="itinerary_destinations",
        many=True,
        read_only=True,
    )

    class Meta:
        model = Itinerary
        fields = [
            "id",
            "user",
            "base_itinerary",
            "main_destination",
            "main_destination_id",
            "title",
            "summary",
            "total_days",
            "budget_min",
            "budget_max",
            "travel_style",
            "source_type",
            "status",
            "is_fixed",
            "is_public",
            "created_at",
            "updated_at",
            "destinations_detail",
        ]
        read_only_fields = [
            "id",
            "user",
            "main_destination",
            "created_at",
            "updated_at",
        ]


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "username", "date_joined", "last_login"]


# =========================
#  REVIEWS / AIRPORT / FLIGHTS / PREFERENCES
# =========================
class ItineraryReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ItineraryReview
        fields = [
            "id",
            "itinerary",
            "user",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["id", "code", "name", "city", "country"]
        read_only_fields = ["id"]


class FlightSegmentSerializer(serializers.ModelSerializer):
    origin_airport_id = serializers.PrimaryKeyRelatedField(
        source="origin_airport",
        queryset=Airport.objects.all(),
        write_only=True,
        required=True,
    )
    destination_airport_id = serializers.PrimaryKeyRelatedField(
        source="destination_airport",
        queryset=Airport.objects.all(),
        write_only=True,
        required=True,
    )
    origin_airport = AirportSerializer(read_only=True)
    destination_airport = AirportSerializer(read_only=True)

    class Meta:
        model = FlightSegment
        fields = [
            "id",
            "origin_airport",
            "origin_airport_id",
            "destination_airport",
            "destination_airport_id",
            "airline",
            "flight_number",
            "departure_time",
            "arrival_time",
            "price",
        ]
        read_only_fields = ["id", "origin_airport", "destination_airport"]


class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preference
        fields = ["id", "name"]
        read_only_fields = ["id"]


class UserPreferenceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    preference = PreferenceSerializer(read_only=True)
    preference_id = serializers.PrimaryKeyRelatedField(
        source="preference",
        queryset=Preference.objects.all(),
        write_only=True,
        required=True,
    )

    class Meta:
        model = UserPreference
        fields = ["id", "user", "preference", "preference_id"]
        read_only_fields = ["id", "user", "preference"]
