from rest_framework import serializers
from django.db.models import Q
from django.contrib.auth.models import User

from .models import (
    ChatTurn,
    AIItineraryDraft,
    Destination,
    Service,
    WeatherInfo,
    Itinerary,
    ItineraryDestination,
    ItineraryReview,
    AIDraftReview,
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


class AIItineraryDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIItineraryDraft
        fields = [
            "id",
            "user",
            "text_user",
            "ai_raw",
            "ai_payload",
            "status",
            "is_public",
            "share_requested",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
        ]


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


class ServiceSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "service_type",
            "description",
            "address",
            "price_from",
            "price_range",
            "rating_avg",
            "rating_count",
            "image_url",
        ]
        read_only_fields = fields


class WeatherInfoSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherInfo
        fields = [
            "id",
            "month",
            "note",
        ]
        read_only_fields = fields


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


class ItinerarySummarySerializer(serializers.ModelSerializer):
    main_destination = DestinationSerializer(read_only=True)
    origin_destination = DestinationSerializer(read_only=True)
    destination_destination = DestinationSerializer(read_only=True)

    class Meta:
        model = Itinerary
        fields = [
            "id",
            "title",
            "summary",
            "total_days",
            "source_type",
            "status",
            "is_public",
            "main_destination",
            "origin_destination",
            "destination_destination",
            "created_at",
        ]
        read_only_fields = fields


class ItinerarySerializer(serializers.ModelSerializer):
    main_destination = DestinationSerializer(read_only=True)
    main_destination_id = serializers.PrimaryKeyRelatedField(
        source="main_destination",
        queryset=Destination.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    origin_destination = DestinationSerializer(read_only=True)
    origin_destination_id = serializers.PrimaryKeyRelatedField(
        source="origin_destination",
        queryset=Destination.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    destination_destination = DestinationSerializer(read_only=True)
    destination_destination_id = serializers.PrimaryKeyRelatedField(
        source="destination_destination",
        queryset=Destination.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    origin_airport = AirportSerializer(read_only=True)
    origin_airport_id = serializers.PrimaryKeyRelatedField(
        source="origin_airport",
        queryset=Airport.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    destination_airport = AirportSerializer(read_only=True)
    destination_airport_id = serializers.PrimaryKeyRelatedField(
        source="destination_airport",
        queryset=Airport.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    base_itinerary = serializers.PrimaryKeyRelatedField(
        queryset=Itinerary.objects.all(),
        required=False,
        allow_null=True,
    )

    services = ServiceSerializer(many=True, read_only=True)
    service_ids = serializers.PrimaryKeyRelatedField(
        source="services",
        queryset=Service.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    flight_segments = FlightSegmentSerializer(many=True, read_only=True)
    flight_segment_ids = serializers.PrimaryKeyRelatedField(
        source="flight_segments",
        queryset=FlightSegment.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    destinations_detail = ItineraryDestinationSerializer(
        source="itinerary_destinations",
        many=True,
        read_only=True,
    )
    destinations_input = ItineraryDestinationSerializer(
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Itinerary
        fields = [
            "id",
            "user",
            "base_itinerary",
            "main_destination",
            "main_destination_id",
            "origin_destination",
            "origin_destination_id",
            "destination_destination",
            "destination_destination_id",
            "origin_airport",
            "origin_airport_id",
            "destination_airport",
            "destination_airport_id",
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
            "services",
            "service_ids",
            "flight_segments",
            "flight_segment_ids",
            "created_at",
            "updated_at",
            "destinations_detail",
            "destinations_input",
        ]
        read_only_fields = [
            "id",
            "user",
            "main_destination",
            "origin_destination",
            "destination_destination",
            "origin_airport",
            "destination_airport",
            "services",
            "flight_segments",
            "created_at",
            "updated_at",
        ]

    def _is_admin(self):
        request = self.context.get("request")
        return bool(request and request.user and request.user.is_superuser)

    def validate(self, attrs):
        if not self._is_admin() and self.instance is None:
            if attrs.get("origin_destination") is None:
                raise serializers.ValidationError(
                    {"origin_destination_id": "origin_destination_id is required."}
                )
        return attrs

    def create(self, validated_data):
        if not self._is_admin():
            validated_data["source_type"] = "custom"
            validated_data["is_fixed"] = False
            validated_data["is_public"] = False
        destinations_input = validated_data.pop("destinations_input", [])
        services = validated_data.pop("services", [])
        flight_segments = validated_data.pop("flight_segments", [])
        itinerary = Itinerary.objects.create(**validated_data)
        if services:
            itinerary.services.set(services)
        if flight_segments:
            itinerary.flight_segments.set(flight_segments)
        if destinations_input:
            self._replace_destinations(itinerary, destinations_input)
        return itinerary

    def update(self, instance, validated_data):
        if not self._is_admin():
            validated_data.pop("source_type", None)
            validated_data.pop("is_fixed", None)
            validated_data.pop("is_public", None)
        destinations_input = validated_data.pop("destinations_input", None)
        services = validated_data.pop("services", None)
        flight_segments = validated_data.pop("flight_segments", None)
        instance = super().update(instance, validated_data)
        if services is not None:
            instance.services.set(services)
        if flight_segments is not None:
            instance.flight_segments.set(flight_segments)
        if destinations_input is not None:
            self._replace_destinations(instance, destinations_input)
        return instance

    @staticmethod
    def _replace_destinations(itinerary, items):
        ItineraryDestination.objects.filter(itinerary=itinerary).delete()
        for item in items:
            ItineraryDestination.objects.create(itinerary=itinerary, **item)


class DestinationDetailSerializer(DestinationSerializer):
    services = ServiceSummarySerializer(many=True, read_only=True)
    weather_infos = WeatherInfoSummarySerializer(many=True, read_only=True)
    itineraries = serializers.SerializerMethodField()

    class Meta(DestinationSerializer.Meta):
        fields = DestinationSerializer.Meta.fields + [
            "services",
            "weather_infos",
            "itineraries",
        ]

    def get_itineraries(self, obj):
        request = self.context.get("request")
        qs = Itinerary.objects.filter(
            Q(main_destination=obj) | Q(itinerary_destinations__destination=obj)
        ).distinct()
        if request and request.user and request.user.is_authenticated:
            qs = qs.filter(Q(is_public=True) | Q(user=request.user))
        else:
            qs = qs.filter(is_public=True)
        return ItinerarySummarySerializer(qs.order_by("-created_at"), many=True).data


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


class AIDraftReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AIDraftReview
        fields = [
            "id",
            "draft",
            "user",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]


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
