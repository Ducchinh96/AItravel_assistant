from django.urls import path
from . import views
from .views import  ForgotPasswordView, RegisterView, LoginView, LogoutView, ResetPasswordView

urlpatterns = [
    # Corrected endpoint: '/api/suggest-trip/' (was misspelled 'suggets')
    # Use the class-based APIView so POST is handled properly
    path('api/suggest-trip/', views.TravelPromptAPIView.as_view(), name='suggest-trip'),
    path("api/chat-turns/history/<int:pk>/", views.ChatTurnHistoryAPIView.as_view(), name="chatturn-history"),
    #Đăng ký
    path('api/register/', RegisterView.as_view(), name='register'),
    #Đăng nhập
    path('api/login/', LoginView.as_view(), name='login'),
    #Đăng xuất
    path('api/logout/', LogoutView.as_view(), name='logout'),
    #Quên mật khẩu
    path('api/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('api/reset-password/',ResetPasswordView.as_view(), name='reset-password'),

    #tao lich trinh
    path('api/itineraries/', views.ItineraryListCreateView.as_view(), name='itinerary-list-create'),
    path('api/itineraries/public/', views.PublicItineraryListView.as_view(), name='public-itinerary-list'),

    #edit lich trinh
    path('api/itineraries/<int:pk>/', views.ItineraryDetailView.as_view(), name='itinerary-detail'),
    #quản lý địa điểm du lịch
    path('api/destinations/', views.DestinationListCreateView.as_view(), name='destination-list-create'),
    path('api/destinations/<int:pk>/', views.DestinationDetailView.as_view(), name='destination-detail')
]
