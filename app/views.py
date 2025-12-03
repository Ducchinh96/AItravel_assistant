
from app.models import ChatTurn, Itinerary
from .serializers import ChatTurnSerializer, ResetPasswordSerializer, ItinerarySerializer
from .utils.api_ai import ask_ai   
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from rest_framework import generics, status, permissions
from .permission import IsOwnerOrReadOnly
from rest_framework.decorators import api_view
import random
import os
import string
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.core.cache import cache



class TravelPromptAPIView(APIView):
    """
    POST /api/suggest-trip/
    Body: { "text_user": "..." }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        text_user = (request.data.get("text_user") or "").strip()
        if not text_user:
            return Response({"ok": False, "error": "Missing field: text_user"}, status=400)

        # USER WRAPPER (tư vấn du lịch đầy đủ + tương tác thân thiện)
        user_wrapper = f"""
Người dùng: "{text_user}"

Mục tiêu:
- Đóng vai CHUYÊN GIA TƯ VẤN DU LỊCH thân thiện, nói chuyện tự nhiên, ngắn gọn – rõ ràng.
- Nếu người dùng nêu MỘT ĐỊA ĐIỂM cụ thể, hãy lập tức nêu các ĐIỂM ĐẶC SẮC của nơi đó:
  • Ăn uống: món đặc sản nên thử + vài khu/quán gợi ý theo từng buổi.
  • Vui chơi/giải trí: nên đi đâu, trải nghiệm gì (ngày/đêm), mẹo xếp lịch hợp lý.
  • “Nên đi đâu tiếp theo”: đề xuất 1–2 điểm lân cận để tối ưu di chuyển.
- Nếu câu hỏi nghiêng về THỜI TIẾT hoặc mảng chuyên biệt:
  • Trả lời thân thiện như một LỄ TÂN khách sạn (check-in/out, khu vực ở), 
    một ĐẦU BẾP (đặc sản, quán, khoảng giá), 
    một NHÀ DỰ BÁO THỜI TIẾT (nhiệt độ, mưa/gió theo mùa, mang gì), 
    một HƯỚNG DẪN VUI CHƠI (vé, giờ mở cửa, xếp hàng, mẹo tránh đông).


1) Khi có một thông tin nào đó thì bạn hãy:
2) LỊCH TRÌNH THEO NGÀY (sáng/chiều/tối) kèm thời gian di chuyển ước tính giữa các điểm.
3) KHÁCH SẠN:
   - 2–3 khu vực nên ở + lý do (gần biển/điểm tham quan/ăn uống…).
   - 2–3 gợi ý khách sạn theo hạng (tiết kiệm/tầm trung/cao cấp) + khoảng giá/điểm mạnh.
   - Nếu phân vân, đưa TIÊU CHÍ chọn nhanh (vị trí, mức giá, yên tĩnh vs sôi động).
4) ẨM THỰC:
   - Món đặc sản + 2–3 khu/điểm ăn uống phù hợp theo lịch trình (gợi ý từng bữa nếu được).
5) THỜI TIẾT & RỦI RO MÙA:
   - Dự báo theo thời điểm đi + vật dụng nên mang + phương án dự phòng khi mưa/xấu trời.
6) CHI PHÍ ƯỚC TÍNH (mỗi người):
   - Di chuyển, lưu trú/đêm, ăn/ngày, vé tham quan chính (khoảng giá thực tế).
7) BƯỚC TIẾP THEO:
   - Đưa 1–2 câu hỏi gợi mở để tiếp tục tư vấn sâu (vd: “Bạn muốn ở gần biển hay trung tâm?” “Ngân sách phòng/đêm mong muốn?”).

Yêu cầu trình bày:
- Dùng gạch đầu dòng, súc tích, thực dụng. Nếu có giờ mở cửa/vé thì nêu rõ.
- Ưu tiên bối cảnh Việt Nam trừ khi người dùng chỉ định nơi khác.
"""


        ai_text = (ask_ai(user_wrapper) or "").strip()

        turn = ChatTurn.objects.create(text_user=text_user, text_ai=ai_text)

        return Response({
            "ok": True,
            "data": {
                "text_user": text_user,
                "text_ai": ai_text,
                "saved_chat_turn": {"id": turn.id, "created_at": turn.created_at.isoformat()}
            }
        }, status=200)


class ChatTurnHistoryAPIView(APIView):
    """
    GET /api/chat-turns/history/<pk>/?limit=20
    Trả về: các ChatTurn có id <= pk (mặc định lấy 20 bản ghi gần nhất),
    sắp xếp theo id tăng dần để FE hiển thị đúng thứ tự.
    """
    permission_classes = [AllowAny]

    def get(self, request, pk: int):
        get_object_or_404(ChatTurn, pk=pk)  # đảm bảo pk tồn tại

        try:
            limit = int(request.query_params.get("limit", 20))
        except ValueError:
            limit = 20
        limit = max(1, min(limit, 200))  # giới hạn an toàn

        qs = ChatTurn.objects.filter(id__lte=pk).order_by("-id")[:limit]
        items = list(reversed(qs))  # chuyển lại thứ tự tăng dần
        data = ChatTurnSerializer(items, many=True).data

        return Response({
            "ok": True,
            "params": {"pk": pk, "limit": limit},
            "count": len(data),
            "items": data
        }, status=200)

##SingUp
class RegisterView(APIView):
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
    def post(self, request):
        data = request.data
        email = data.get('email'); password = data.get('password')
        try:
            user = User.objects.get(email=email)
            auth_user = authenticate(request, username=user.username, password=password)
            if auth_user is None:
                return Response({'message': 'Invalid password!'}, status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(auth_user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),   # <--- thêm dòng này
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
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
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
        user.set_password(new_password); user.save()
        cache.delete(f"password_reset_code_{email}")
        return Response({'message': 'Password has been reset successfully!'}, status=status.HTTP_200_OK)

def is_admin(user): return user.is_authenticated and user.is_superuser

#tao lich trinh
class ItineraryListCreateView(generics.ListCreateAPIView):
    serializer_class = ItinerarySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Itinerary.objects.all()
        is_fixed = self.request.query_params.get('is_fixed')
        if is_fixed is not None:
            if is_fixed.lower() in ['true', '1']:
                queryset = queryset.filter(is_fixed=True)
            elif is_fixed.lower() in ['false', '0']:
                queryset = queryset.filter(is_fixed=False)
        return queryset

    def perform_create(self, serializer):
        # If user is authenticated, assign the user. Otherwise leave it null (or handle as needed)
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()
class PublicItineraryListView(generics.ListAPIView):
    """
    Public Community Feed - List all public itineraries
    Anyone can view (no authentication required)
    """
    serializer_class = ItinerarySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Only show public itineraries, ordered by newest first
        return Itinerary.objects.filter(is_public=True).order_by('-created_at')

class ItineraryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Itinerary.objects.all()
    serializer_class = ItinerarySerializer
    permission_classes = [IsOwnerOrReadOnly]