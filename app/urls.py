from django.urls import path
from . import views
from .views import (
    ForgotPasswordView,
    ResetPasswordView,
    RegisterView,
    LoginView,
    LogoutView,
    HotelListCreateView,
    HotelDetailView,
    ServiceListCreateView,
    ServiceDetailView,
    WeatherInfoListCreateView,
    WeatherInfoDetailView,
)

urlpatterns = [
    # Gợi ý lịch trình từ AI
    path('api/suggest-trip/', views.TravelPromptAPIView.as_view(), name='suggest-trip'),
    path("api/chat-turns/history/<int:pk>/", views.ChatTurnHistoryAPIView.as_view(), name="chatturn-history"),

    # Đăng ký / đăng nhập / đăng xuất
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),

    # Quên mật khẩu / đặt lại mật khẩu
    path('api/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('api/reset-password/', ResetPasswordView.as_view(), name='reset_password'),

    # Lịch trình
    path('api/itineraries/', views.ItineraryListCreateView.as_view(), name='itinerary-list-create'),
    path('api/itineraries/public/', views.PublicItineraryListView.as_view(), name='public-itinerary-list'),
    path('api/itineraries/<int:pk>/', views.ItineraryDetailView.as_view(), name='itinerary-detail'),

    # Hồ sơ người dùng
    path('api/profile/', views.UserProfileView.as_view(), name='user-profile'),

    # Điểm đến
    path('api/destinations/', views.DestinationListCreateView.as_view(), name='destination-list-create'),
    path('api/destinations/<int:pk>/', views.DestinationDetailView.as_view(), name='destination-detail'),

    # Khách sạn
    path('api/hotels/', HotelListCreateView.as_view(), name='hotel-list-create'),
    path('api/hotels/<int:pk>/', HotelDetailView.as_view(), name='hotel-detail'),

    # Dịch vụ
    path('api/services/', ServiceListCreateView.as_view(), name='service-list-create'),
    path('api/services/<int:pk>/', ServiceDetailView.as_view(), name='service-detail'),

    # Thời tiết theo điểm đến
    path('api/weather/', WeatherInfoListCreateView.as_view(), name='weatherinfo-list-create'),
    path('api/weather/<int:pk>/', WeatherInfoDetailView.as_view(), name='weatherinfo-detail'),

    # Admin
    path('api/admin/users/', views.AdminUserListView.as_view(), name='admin-user-list'),
    path('api/admin/users/<int:pk>/', views.AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('api/admin/statistics/', views.AdminStatisticsView.as_view(), name='admin-statistics'),
]
