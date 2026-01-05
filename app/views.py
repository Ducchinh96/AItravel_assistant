from app.models import (
    ChatTurn,
    AIItineraryDraft,
    Itinerary,
    Destination,
    ItineraryDestination,
    Service,
    WeatherInfo,
    ItineraryReview,
    AIDraftReview,
    Airport,
    FlightSegment,
    Preference,
    UserPreference,
)

from .serializers import (
    ChatTurnSerializer,
    AIItineraryDraftSerializer,
    ItinerarySerializer,
    UserSerializer,
    DestinationSerializer,
    DestinationDetailSerializer,
    AdminUserSerializer,
    ResetPasswordSerializer,
    ServiceSerializer,
    WeatherInfoSerializer,
    ItineraryReviewSerializer,
    AIDraftReviewSerializer,
    AirportSerializer,
    FlightSegmentSerializer,
    PreferenceSerializer,
    UserPreferenceSerializer,
)

from .utils.api_ai import ask_ai

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import generics, status, permissions

from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.core.cache import cache

from .permissions import IsOwnerOrReadOnly

import random
import string
import json
from string import Template
from textwrap import dedent


# ========= HELPER: Parse JSON AI trả về an toàn =========
def parse_ai_itinerary_json(ai_text: str):
    """
    Thử parse JSON từ chuỗi AI trả về.
    - Ưu tiên json.loads toàn bộ chuỗi.
    - Nếu fail, thử cắt từ '{' đầu tới '}' cuối rồi parse.
    - Nếu vẫn fail thì trả None.
    """
    if not ai_text:
        return None

    # Thử parse trực tiếp
    try:
        return json.loads(ai_text)
    except json.JSONDecodeError:
        pass

    # Thử cắt từ { ... } nếu AI lỡ thêm text linh tinh
    first = ai_text.find("{")
    last = ai_text.rfind("}")
    if first != -1 and last != -1 and last > first:
        candidate = ai_text[first:last + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            return None

    return None





def _coerce_float(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
# ========= HELPER: Map schedule -> ItineraryDestination (theo model mới) =========
def sync_itinerary_destinations_from_ai(itinerary: Itinerary, ai_data: dict):
    """
    Dựa trên JSON AI, tạo các bản ghi ItineraryDestination để fit với bảng Destination
    và ItineraryDestination mới.

    Kỳ vọng format "schedule" kiểu:

    "schedule": [
      {
        "day_number": 1,
        "morning": [
          {
            "destination_name": "Chợ Đà Lạt",
            "activity_title": "Tham quan chợ",
            "activity_description": "Dạo chợ, chụp hình, ăn vặt nhẹ."
          }
        ],
        "afternoon": [ ... ],
        "evening": [ ... ]
      },
      ...
    ]

    - day_number: nếu thiếu thì fallback sang "day" hoặc index trong list.
    - Nếu thiếu destination_name thì bỏ qua slot đó.
    - Destination sẽ được get_or_create theo name (các field khác để trống).
    """
    if not isinstance(ai_data, dict):
        return

    schedule = ai_data.get("schedule") or []
    if not isinstance(schedule, list):
        return

    part_map = {
        "morning": "s?ng",
        "afternoon": "chi?u",
        "evening": "t?i",
        "full_day": "c? ng?y",
    }

    for idx_day, day_block in enumerate(schedule, start=1):
        if not isinstance(day_block, dict):
            continue

        day_number = day_block.get("day_number") or day_block.get("day") or idx_day

        for part_of_day in ["morning", "afternoon", "evening", "full_day"]:
            activities = day_block.get(part_of_day) or []
            if not isinstance(activities, list):
                continue

            for index, item in enumerate(activities, start=1):
                if not isinstance(item, dict):
                    continue

                dest_name = (item.get("destination_name") or item.get("destination") or "").strip()
                if not dest_name:
                    continue

                dest_lat = _coerce_float(
                    item.get("latitude")
                    or item.get("lat")
                    or item.get("destination_latitude")
                    or item.get("destination_lat")
                )
                dest_lng = _coerce_float(
                    item.get("longitude")
                    or item.get("lng")
                    or item.get("lon")
                    or item.get("destination_longitude")
                    or item.get("destination_lng")
                )

                defaults = {
                    "short_description": "",
                    "location": "",
                    "image_url": None,
                }
                if dest_lat is not None:
                    defaults["latitude"] = dest_lat
                if dest_lng is not None:
                    defaults["longitude"] = dest_lng

                # tìm hoặc tạo Destination theo tên
                dest, created = Destination.objects.get_or_create(
                    name=dest_name,
                    defaults=defaults,
                )
                if not created:
                    update_fields = []
                    if dest_lat is not None and dest.latitude is None:
                        dest.latitude = dest_lat
                        update_fields.append("latitude")
                    if dest_lng is not None and dest.longitude is None:
                        dest.longitude = dest_lng
                        update_fields.append("longitude")
                    if update_fields:
                        dest.save(update_fields=update_fields)

                activity_title = (
                    item.get("activity_title")
                    or item.get("activity")
                    or dest_name
                )
                activity_description = (
                    item.get("activity_description")
                    or item.get("activity")
                    or ""
                )

                ItineraryDestination.objects.create(
                    itinerary=itinerary,
                    destination=dest,
                    day_number=day_number,
                    part_of_day=part_map.get(part_of_day, part_of_day),
                    activity_title=activity_title,
                    activity_description=activity_description,
                    order=index,
                )



# ========= HELPER: Create Itinerary from AI JSON =========
def create_itinerary_from_ai(user, ai_json: dict):
    if not isinstance(ai_json, dict):
        raise ValueError("Invalid AI JSON")

    schedule = ai_json.get("schedule") or []
    has_schedule = isinstance(schedule, list) and len(schedule) > 0

    total_days = ai_json.get("total_days")
    if not isinstance(total_days, int) or total_days <= 0:
        if has_schedule:
            total_days = len(schedule)
        else:
            total_days = 1

    main_destination = None
    main_dest_name = (ai_json.get("main_destination_name") or "").strip()
    if main_dest_name:
        main_lat = _coerce_float(
            ai_json.get("main_destination_latitude")
            or ai_json.get("main_destination_lat")
        )
        main_lng = _coerce_float(
            ai_json.get("main_destination_longitude")
            or ai_json.get("main_destination_lng")
            or ai_json.get("main_destination_lon")
        )
        if isinstance(ai_json.get("main_destination"), dict):
            main_lat = _coerce_float(
                ai_json["main_destination"].get("latitude")
                or ai_json["main_destination"].get("lat")
            ) or main_lat
            main_lng = _coerce_float(
                ai_json["main_destination"].get("longitude")
                or ai_json["main_destination"].get("lng")
                or ai_json["main_destination"].get("lon")
            ) or main_lng

        defaults = {
            "short_description": "",
            "location": "",
            "image_url": None,
        }
        if main_lat is not None:
            defaults["latitude"] = main_lat
        if main_lng is not None:
            defaults["longitude"] = main_lng

        main_destination, created = Destination.objects.get_or_create(
            name=main_dest_name,
            defaults=defaults,
        )
        if not created:
            update_fields = []
            if main_lat is not None and main_destination.latitude is None:
                main_destination.latitude = main_lat
                update_fields.append("latitude")
            if main_lng is not None and main_destination.longitude is None:
                main_destination.longitude = main_lng
                update_fields.append("longitude")
            if update_fields:
                main_destination.save(update_fields=update_fields)

    itinerary_instance = Itinerary.objects.create(
        user=user,
        base_itinerary=None,
        main_destination=main_destination,
        title=ai_json.get("title", "AI itinerary"),
        summary=ai_json.get("summary", "") or "",
        total_days=total_days,
        budget_min=None,
        budget_max=None,
        travel_style=ai_json.get("travel_style", "") or "",
        source_type="ai",
        status="published",
        is_fixed=False,
        is_public=False,
    )

    if has_schedule:
        sync_itinerary_destinations_from_ai(itinerary_instance, ai_json)

    return itinerary_instance


# ========== AI GỢI Ý LỊCH TRÌNH ==========

class TravelPromptAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        text_user = (request.data.get("text_user") or "").strip()
        if not text_user:
            return Response({"ok": False, "error": "Missing field: text_user"}, status=400)

        # PROMPT mới: khớp với model mới (Itinerary + ItineraryDestination)
        # Prompt: return JSON that fits current DB models
        # Prompt: return JSON that fits current DB models, adapt to user details if provided
        user_wrapper = Template(dedent(r'''\
User: "$text_user"

Role: Professional travel advisor.
Goal: Return ONLY valid JSON (no markdown, no extra text).

Behavior rules:
- If user provides origin, destination, dates, budget, preferences, or constraints, use them directly.
- If any key info is missing, infer reasonable defaults and clearly reflect them in the response.
- Use specific place names that match the user request.
- Include latitude and longitude (decimal degrees) for main destination and each activity destination when possible.
- If user only asks general questions, set schedule = [] and focus on chat_response.
 - For flight_segments: always include airline, flight_number, departure_time, arrival_time, and price when possible.
 - For services: include address and image_url if available; keep descriptions short and useful.

JSON schema (keys required):
{
  "title": "string",
  "summary": "string",
  "total_days": 3,
  "main_destination_name": "string",
  "main_destination_latitude": 0.0,
  "main_destination_longitude": 0.0,
  "travel_style": "string",
  "schedule": [
    {
      "day_number": 1,
      "morning": [
        {
          "destination_name": "string",
          "latitude": 0.0,
          "longitude": 0.0,
          "activity_title": "string",
          "activity_description": "string"
        }
      ],
      "afternoon": [ {"destination_name": "string", "latitude": 0.0, "longitude": 0.0, "activity_title": "string", "activity_description": "string"} ],
      "evening": [ {"destination_name": "string", "latitude": 0.0, "longitude": 0.0, "activity_title": "string", "activity_description": "string"} ]
    }
  ],
  "airports": [
    { "code": "string", "name": "string", "city": "string", "country": "string" }
  ],
  "flight_segments": [
    {
      "origin_airport_code": "string",
      "destination_airport_code": "string",
      "airline": "string",
      "flight_number": "string",
      "departure_time": "YYYY-MM-DDTHH:MM:SSZ",
      "arrival_time": "YYYY-MM-DDTHH:MM:SSZ",
      "price": 0
    }
  ],
  "services": [
    {
      "destination_name": "string",
      "service_type": "hotel|food|spa|activity|shopping|other",
      "name": "string",
      "description": "string",
      "address": "string",
      "price_from": 0,
      "price_range": "string",
      "rating_avg": 0,
      "rating_count": 0,
      "image_url": "string"
    }
  ],
  "weather": [
    { "destination_name": "string", "month": 1, "note": "string" }
  ],
  "preferences": ["string"],
  "chat_response": "string"
}

Constraints:
- total_days must be an integer and match schedule length when possible.
- service_type must be one of the allowed values.
- airport code should be IATA if applicable.
- No markdown or code fences.
''')).substitute(text_user=text_user)
        ai_text = (ask_ai(user_wrapper) or "").strip()

        # Lưu ChatTurn (user chắc chắn đã đăng nhập)
        user = request.user
        turn = ChatTurn.objects.create(
            text_user=text_user,
            text_ai=ai_text,
            user=user
        )

        ai_json = parse_ai_itinerary_json(ai_text)

        draft = AIItineraryDraft.objects.create(
            user=user,
            text_user=text_user,
            ai_raw=ai_text,
            ai_payload=ai_json if isinstance(ai_json, dict) else None,
            status="pending",
        )

        response_data = {
            "text_user": text_user,
            "text_ai": ai_text,
            "saved_chat_turn": {
                "id": turn.id,
                "created_at": turn.created_at.isoformat()
            },
            "draft": {
                "id": draft.id,
                "status": draft.status,
                "created_at": draft.created_at.isoformat()
            }
        }

        if isinstance(ai_json, dict):
            response_data["ai_payload"] = ai_json
            if "chat_response" in ai_json:
                response_data["chat_response"] = ai_json.get("chat_response")

        return Response({
            "ok": True,
            "data": response_data
        }, status=200)


class ChatTurnHistoryAPIView(APIView):
    """
    GET /api/chat-turns/history/<pk>/?limit=20

    Trả về các ChatTurn của CHÍNH USER hiện tại
    có id <= pk (mặc định lấy 20 bản ghi gần nhất),
    sắp xếp theo id tăng dần để FE hiển thị đúng thứ tự.

    YÊU CẦU: PHẢI ĐĂNG NHẬP
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk: int):
        user = request.user

        # Đảm bảo pk tồn tại và thuộc về user (hoặc admin thì bỏ qua)
        if user.is_superuser:
            get_object_or_404(ChatTurn, pk=pk)
        else:
            get_object_or_404(ChatTurn, pk=pk, user=user)

        try:
            limit = int(request.query_params.get("limit", 20))
        except ValueError:
            limit = 20
        limit = max(1, min(limit, 200))  # giới hạn an toàn

        qs = ChatTurn.objects.all()
        if not user.is_superuser:
            qs = qs.filter(user=user)

        qs = qs.filter(id__lte=pk).order_by("-id")[:limit]
        items = list(reversed(qs))  # chuyển lại thứ tự tăng dần
        data = ChatTurnSerializer(items, many=True).data

        return Response({
            "ok": True,
            "params": {"pk": pk, "limit": limit},
            "count": len(data),
            "items": data
        }, status=200)



class ItineraryDraftListView(generics.ListAPIView):
    serializer_class = AIItineraryDraftSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = AIItineraryDraft.objects.all()
        user = self.request.user
        if not user.is_superuser:
            qs = qs.filter(user=user)
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)
        is_public = self.request.query_params.get("is_public")
        if is_public is not None:
            if is_public.lower() in ["true", "1"]:
                qs = qs.filter(is_public=True)
            elif is_public.lower() in ["false", "0"]:
                qs = qs.filter(is_public=False)
        return qs


class ItineraryDraftDetailView(generics.RetrieveAPIView):
    serializer_class = AIItineraryDraftSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = AIItineraryDraft.objects.all()
        user = self.request.user
        if not user.is_superuser:
            qs = qs.filter(user=user)
        return qs


class ItineraryDraftAcceptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk: int):
        draft = get_object_or_404(AIItineraryDraft, pk=pk)
        user = request.user
        if not user.is_superuser and draft.user_id != user.id:
            return Response({"ok": False, "error": "Forbidden"}, status=403)

        if draft.status == "accepted":
            return Response({
                "ok": True,
                "draft": AIItineraryDraftSerializer(draft).data,
            }, status=200)

        ai_json = draft.ai_payload or parse_ai_itinerary_json(draft.ai_raw)
        if not isinstance(ai_json, dict):
            return Response({"ok": False, "error": "Invalid AI data"}, status=400)

        draft.status = "accepted"
        draft.is_public = False
        draft.share_requested = False
        draft.save(update_fields=["status", "is_public", "share_requested", "updated_at"])

        return Response({
            "ok": True,
            "draft": AIItineraryDraftSerializer(draft).data,
        }, status=200)


class ItineraryDraftRejectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk: int):
        draft = get_object_or_404(AIItineraryDraft, pk=pk)
        user = request.user
        if not user.is_superuser and draft.user_id != user.id:
            return Response({"ok": False, "error": "Forbidden"}, status=403)

        draft.status = "rejected"
        draft.is_public = False
        draft.share_requested = False
        draft.save(update_fields=["status", "is_public", "share_requested", "updated_at"])

        return Response({"ok": True, "draft": AIItineraryDraftSerializer(draft).data}, status=200)


# ========== AUTH ==========

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        username = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')

        if password != confirm_password:
            return Response({'error': 'Passwords do not match!'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Email already exists!'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username, email=username, password=password,
            first_name=first_name, last_name=last_name
        )
        return Response({'message': 'User registered successfully!'}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        try:
            user = User.objects.get(email=email)
            auth_user = authenticate(request, username=user.username, password=password)
            if auth_user is None:
                return Response({'message': 'Invalid password!'}, status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(auth_user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': auth_user.id,
                    'first_name': auth_user.first_name,
                    'last_name': auth_user.last_name,
                    'email': auth_user.email,
                    'is_superuser': auth_user.is_superuser,
                }
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'User with this email does not exist!'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist!'}, status=status.HTTP_404_NOT_FOUND)

        code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        cache.set(f"password_reset_code_{email}", code, timeout=600)

        try:
            send_mail(
                subject="Confirmation Code - Bookquest",
                message=f"Hello {user.first_name},\n\nYour confirmation code is: {code}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            return Response({'message': 'Confirmation code sent to your email!'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Failed to send email.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        confirmation_code = serializer.validated_data['confirmation_code']
        new_password = serializer.validated_data['new_password']

        cached_code = cache.get(f"password_reset_code_{email}")
        if not cached_code or cached_code != confirmation_code:
            return Response({'error': 'Invalid or expired confirmation code!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist!'}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()
        cache.delete(f"password_reset_code_{email}")
        return Response({'message': 'Password has been reset successfully!'}, status=status.HTTP_200_OK)


def is_admin(user):
    return user.is_authenticated and user.is_superuser


# ========== ITINERARY & DESTINATION CRUD ==========

class ItineraryListCreateView(generics.ListCreateAPIView):
    """
    - GET /api/itineraries/: trả về các lịch trình của CHÍNH USER hiện tại.
      + Admin thì thấy tất cả.
    - POST /api/itineraries/: tạo mới, tự gán user = request.user.

    YÊU CẦU: PHẢI ĐĂNG NHẬP
    """
    serializer_class = ItinerarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Itinerary.objects.all()
        user = self.request.user

        if not user.is_superuser:
            qs = qs.filter(user=user)

        is_fixed = self.request.query_params.get('is_fixed')
        if is_fixed is not None:
            if is_fixed.lower() in ['true', '1']:
                qs = qs.filter(is_fixed=True)
            elif is_fixed.lower() in ['false', '0']:
                qs = qs.filter(is_fixed=False)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ItineraryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    - GET: xem chi tiết lịch trình
    - PUT/PATCH/DELETE: chỉ owner hoặc admin (IsOwnerOrReadOnly)
    """
    queryset = Itinerary.objects.all()
    serializer_class = ItinerarySerializer
    permission_classes = [IsOwnerOrReadOnly]


class PublicItineraryListView(generics.ListAPIView):
    """
    Public Community Feed - List all public itineraries
    Anyone can view (no authentication required)
    """
    serializer_class = ItinerarySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Only show public sample itineraries, ordered by newest first
        return Itinerary.objects.filter(
            is_public=True,
            source_type="sample",
        ).order_by('-created_at')


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class DestinationListCreateView(generics.ListCreateAPIView):
    """
    - GET: ai cũng xem được danh sách điểm đến (dữ liệu mẫu)
    - POST: chỉ admin được phép thêm điểm đến mới
    """
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class DestinationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    - GET: ai cũng xem được chi tiết điểm đến
    - PUT/PATCH/DELETE: chỉ admin
    """
    queryset = Destination.objects.all()
    serializer_class = DestinationDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


# ========== HOTEL (KHÁCH SẠN) ==========

class HotelListCreateView(generics.ListCreateAPIView):
    """
    GET: List khach san (filter ?destination_id=)
    POST: Chi admin duoc phep tao moi
    """
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Service.objects.select_related("destination").filter(
            service_type=Service.ServiceType.HOTEL
        )
        destination_id = self.request.query_params.get("destination_id")
        if destination_id:
            qs = qs.filter(destination_id=destination_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(service_type=Service.ServiceType.HOTEL)

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class HotelDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Xem chi tiet 1 khach san
    PUT/PATCH/DELETE: Chi admin
    """
    queryset = Service.objects.select_related("destination").filter(
        service_type=Service.ServiceType.HOTEL
    )
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        serializer.save(service_type=Service.ServiceType.HOTEL)

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class ServiceListCreateView(generics.ListCreateAPIView):
    """
    GET: List dịch vụ (filter ?destination_id= & ?service_type=)
    POST: Chỉ admin được phép tạo mới
    """
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Service.objects.select_related("destination").all()

        destination_id = self.request.query_params.get("destination_id")
        if destination_id:
            qs = qs.filter(destination_id=destination_id)

        service_type = self.request.query_params.get("service_type")
        if service_type:
            qs = qs.filter(service_type=service_type)

        return qs

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Xem chi tiết 1 dịch vụ
    PUT/PATCH/DELETE: Chỉ admin
    """
    queryset = Service.objects.select_related("destination").all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


# ========== WEATHERINFO (THỜI TIẾT) ==========

class WeatherInfoListCreateView(generics.ListCreateAPIView):
    """
    GET: List thông tin thời tiết (filter ?destination_id=, ?month=)
    POST: Chỉ admin được phép tạo/cập nhật dữ liệu thời tiết
    """
    serializer_class = WeatherInfoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = WeatherInfo.objects.select_related("destination").all()
        destination_id = self.request.query_params.get("destination_id")
        month = self.request.query_params.get("month")

        if destination_id:
            qs = qs.filter(destination_id=destination_id)
        if month:
            try:
                month_int = int(month)
                qs = qs.filter(month=month_int)
            except ValueError:
                pass
        return qs

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class WeatherInfoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Xem chi tiết 1 bản ghi thời tiết
    PUT/PATCH/DELETE: Chỉ admin
    """
    queryset = WeatherInfo.objects.select_related("destination").all()
    serializer_class = WeatherInfoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


# ========== REVIEWS / AIRPORTS / FLIGHTS / PREFERENCES ==========

class ItineraryReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ItineraryReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = ItineraryReview.objects.select_related("itinerary", "user").all()
        itinerary_id = self.request.query_params.get("itinerary_id")
        if itinerary_id:
            qs = qs.filter(itinerary_id=itinerary_id)
        user_id = self.request.query_params.get("user_id")
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ItineraryReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ItineraryReview.objects.select_related("itinerary", "user").all()
    serializer_class = ItineraryReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]


class AIDraftReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = AIDraftReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = AIDraftReview.objects.select_related("draft", "user").all()
        draft_id = self.request.query_params.get("draft_id")
        if draft_id:
            qs = qs.filter(draft_id=draft_id)
        user_id = self.request.query_params.get("user_id")
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AIDraftReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AIDraftReview.objects.select_related("draft", "user").all()
    serializer_class = AIDraftReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]


class AirportListCreateView(generics.ListCreateAPIView):
    serializer_class = AirportSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Airport.objects.all().order_by("code")
        destination_id = self.request.query_params.get("destination_id")
        if destination_id:
            qs = qs.filter(destination_id=destination_id)
        return qs

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class AirportDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class FlightSegmentListCreateView(generics.ListCreateAPIView):
    serializer_class = FlightSegmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = FlightSegment.objects.select_related(
            "origin_airport", "destination_airport"
        ).all()
        origin_id = self.request.query_params.get("origin_airport_id")
        if origin_id:
            qs = qs.filter(origin_airport_id=origin_id)
        destination_id = self.request.query_params.get("destination_airport_id")
        if destination_id:
            qs = qs.filter(destination_airport_id=destination_id)
        destination_id = self.request.query_params.get("destination_id")
        if destination_id:
            qs = qs.filter(destination_airport__destination_id=destination_id)
        airline = self.request.query_params.get("airline")
        if airline:
            qs = qs.filter(airline__icontains=airline)
        return qs

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class FlightSegmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FlightSegment.objects.select_related(
        "origin_airport", "destination_airport"
    ).all()
    serializer_class = FlightSegmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class PreferenceListCreateView(generics.ListCreateAPIView):
    queryset = Preference.objects.all().order_by("name")
    serializer_class = PreferenceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class PreferenceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Preference.objects.all()
    serializer_class = PreferenceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class UserPreferenceListCreateView(generics.ListCreateAPIView):
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserPreference.objects.select_related("preference", "user").filter(
            user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserPreferenceDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = UserPreferenceSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return UserPreference.objects.select_related("preference", "user").filter(
            user=self.request.user
        )


# ========== ADMIN ==========

class AdminUserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminStatisticsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)

        # Total counts
        total_users = User.objects.count()
        total_itineraries = Itinerary.objects.count()
        total_destinations = Destination.objects.count()

        # User breakdown
        active_users = User.objects.filter(is_active=True).count()
        inactive_users = User.objects.filter(is_active=False).count()
        admin_users = User.objects.filter(is_superuser=True).count()

        # Recent activity - last 30 days
        new_users_30d = User.objects.filter(date_joined__gte=last_30_days).count()
        new_itineraries_30d = Itinerary.objects.filter(created_at__gte=last_30_days).count()
        new_destinations_30d = Destination.objects.filter(created_at__gte=last_30_days).count()

        # Recent activity - last 7 days
        new_users_7d = User.objects.filter(date_joined__gte=last_7_days).count()
        new_itineraries_7d = Itinerary.objects.filter(created_at__gte=last_7_days).count()

        statistics = {
            "total_counts": {
                "users": total_users,
                "itineraries": total_itineraries,
                "destinations": total_destinations
            },
            "user_breakdown": {
                "active_users": active_users,
                "inactive_users": inactive_users,
                "admin_users": admin_users
            },
            "last_30_days": {
                "new_users": new_users_30d,
                "new_itineraries": new_itineraries_30d,
                "new_destinations": new_destinations_30d
            },
            "last_7_days": {
                "new_users": new_users_7d,
                "new_itineraries": new_itineraries_7d
            }
        }

        return Response({
            "ok": True,
            "statistics": statistics
        }, status=200)


class PublicAIDraftListView(generics.ListAPIView):
    serializer_class = AIItineraryDraftSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return AIItineraryDraft.objects.filter(
            status="accepted",
            is_public=True,
        ).order_by("-created_at")


class AdminAIDraftPublishView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk: int):
        draft = get_object_or_404(AIItineraryDraft, pk=pk)
        if draft.status != "accepted":
            return Response(
                {"ok": False, "error": "Draft must be accepted before publishing."},
                status=400,
            )
        draft.is_public = True
        draft.share_requested = False
        draft.save(update_fields=["is_public", "share_requested", "updated_at"])
        return Response({"ok": True, "draft": AIItineraryDraftSerializer(draft).data}, status=200)


class AdminAIDraftRejectShareView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk: int):
        draft = get_object_or_404(AIItineraryDraft, pk=pk)
        if draft.status != "accepted":
            return Response(
                {"ok": False, "error": "Draft must be accepted before rejecting share."},
                status=400,
            )
        draft.share_requested = False
        draft.is_public = False
        draft.save(update_fields=["is_public", "share_requested", "updated_at"])
        return Response({"ok": True, "draft": AIItineraryDraftSerializer(draft).data}, status=200)


class AIDraftShareRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk: int):
        draft = get_object_or_404(AIItineraryDraft, pk=pk)
        user = request.user
        if not user.is_superuser and draft.user_id != user.id:
            return Response({"ok": False, "error": "Forbidden"}, status=403)
        if draft.status != "accepted":
            return Response({"ok": False, "error": "Draft must be accepted first."}, status=400)
        draft.share_requested = True
        draft.save(update_fields=["share_requested", "updated_at"])
        return Response({"ok": True, "draft": AIItineraryDraftSerializer(draft).data}, status=200)


class AdminAIDraftRequestListView(generics.ListAPIView):
    serializer_class = AIItineraryDraftSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return AIItineraryDraft.objects.filter(
            status="accepted",
            share_requested=True,
        ).order_by("-created_at")


class AdminItineraryApproveView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk: int):
        itinerary = get_object_or_404(Itinerary, pk=pk)
        itinerary.source_type = "sample"
        itinerary.is_fixed = True
        itinerary.is_public = True
        itinerary.status = "published"
        itinerary.save(update_fields=["source_type", "is_fixed", "is_public", "status", "updated_at"])
        return Response({"ok": True, "itinerary": ItinerarySerializer(itinerary).data}, status=200)
