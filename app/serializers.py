from rest_framework import serializers
from django.contrib.auth.models import User

from .models import (
    ChatTurn,
    Destination,
    Hotel,
    Service,
    WeatherInfo,
    Itinerary,
    ItineraryDestination,
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
#  ĐIỂM ĐẾN & CÁC THÔNG TIN LIÊN QUAN
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


class HotelSerializer(serializers.ModelSerializer):
    # Cho phép FE gửi id điểm đến
    destination_id = serializers.PrimaryKeyRelatedField(
        source="destination",
        queryset=Destination.objects.all(),
        write_only=True,
        required=True,
    )
    # Đọc ra thông tin điểm đến cơ bản (tùy bạn dùng hay không)
    destination = DestinationSerializer(read_only=True)

    class Meta:
        model = Hotel
        fields = [
            "id",
            "destination",
            "destination_id",
            "name",
            "address",
            "price_range",
            "image_url",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "destination"]


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
            "id",              # db_column = id_dich_vu
            "destination",
            "destination_id",  # db_column = diem_den_id
            "name",            # db_column = ten_dich_vu
            "service_type",    # db_column = loai_dich_vu
            "description",     # db_column = mo_ta
            "address",         # db_column = dia_chi
            "price_range",     # db_column = gia_tham_khao
            "image_url",       # db_column = hinh_anh
            "created_at",      # db_column = ngay_tao
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
#  LỊCH TRÌNH & CHI TIẾT LỊCH TRÌNH
# =========================
class ItineraryDestinationSerializer(serializers.ModelSerializer):
    # Đọc: embed thông tin điểm đến cho dễ xem
    destination = DestinationSerializer(read_only=True)
    # Ghi: gửi id điểm đến
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
    # main_destination: đọc & ghi tách riêng id
    main_destination = DestinationSerializer(read_only=True)
    main_destination_id = serializers.PrimaryKeyRelatedField(
        source="main_destination",
        queryset=Destination.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    # base_itinerary: chỉ cần id cho clone từ lịch trình mẫu
    base_itinerary = serializers.PrimaryKeyRelatedField(
        queryset=Itinerary.objects.all(),
        required=False,
        allow_null=True,
    )

    # Danh sách chi tiết điểm đến theo ngày/buổi (read-only)
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
