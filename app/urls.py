from django.urls import path
from . import views
from .views import  ForgotPasswordView, ResetPasswordView, RegisterView, LoginView, LogoutView

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
    # #Quên mật khẩu
    # path('api/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    # path('api/reset-password/', ResetPasswordView.as_view(), name='reset_password'),

]
