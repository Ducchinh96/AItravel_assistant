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
    ItineraryReviewListCreateView,
    ItineraryReviewDetailView,
    AirportListCreateView,
    AirportDetailView,
    FlightSegmentListCreateView,
    FlightSegmentDetailView,
    PreferenceListCreateView,
    PreferenceDetailView,
    UserPreferenceListCreateView,
    UserPreferenceDetailView,
)

urlpatterns = [
    path('api/suggest-trip/', views.TravelPromptAPIView.as_view(), name='suggest-trip'),
    path("api/chat-turns/history/<int:pk>/", views.ChatTurnHistoryAPIView.as_view(), name="chatturn-history"),

    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),

    path('api/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('api/reset-password/', ResetPasswordView.as_view(), name='reset_password'),

    path('api/itineraries/', views.ItineraryListCreateView.as_view(), name='itinerary-list-create'),
    path('api/itineraries/public/', views.PublicItineraryListView.as_view(), name='public-itinerary-list'),
    path('api/itineraries/<int:pk>/', views.ItineraryDetailView.as_view(), name='itinerary-detail'),

    path('api/profile/', views.UserProfileView.as_view(), name='user-profile'),

    path('api/destinations/', views.DestinationListCreateView.as_view(), name='destination-list-create'),
    path('api/destinations/<int:pk>/', views.DestinationDetailView.as_view(), name='destination-detail'),

    path('api/hotels/', HotelListCreateView.as_view(), name='hotel-list-create'),
    path('api/hotels/<int:pk>/', HotelDetailView.as_view(), name='hotel-detail'),

    path('api/services/', ServiceListCreateView.as_view(), name='service-list-create'),
    path('api/services/<int:pk>/', ServiceDetailView.as_view(), name='service-detail'),

    path('api/weather/', WeatherInfoListCreateView.as_view(), name='weatherinfo-list-create'),
    path('api/weather/<int:pk>/', WeatherInfoDetailView.as_view(), name='weatherinfo-detail'),

    path('api/itinerary-reviews/', ItineraryReviewListCreateView.as_view(), name='itinerary-review-list-create'),
    path('api/itinerary-reviews/<int:pk>/', ItineraryReviewDetailView.as_view(), name='itinerary-review-detail'),

    path('api/airports/', AirportListCreateView.as_view(), name='airport-list-create'),
    path('api/airports/<int:pk>/', AirportDetailView.as_view(), name='airport-detail'),

    path('api/flight-segments/', FlightSegmentListCreateView.as_view(), name='flight-segment-list-create'),
    path('api/flight-segments/<int:pk>/', FlightSegmentDetailView.as_view(), name='flight-segment-detail'),

    path('api/preferences/', PreferenceListCreateView.as_view(), name='preference-list-create'),
    path('api/preferences/<int:pk>/', PreferenceDetailView.as_view(), name='preference-detail'),

    path('api/user-preferences/', UserPreferenceListCreateView.as_view(), name='user-preference-list-create'),
    path('api/user-preferences/<int:pk>/', UserPreferenceDetailView.as_view(), name='user-preference-detail'),

    path('api/admin/users/', views.AdminUserListView.as_view(), name='admin-user-list'),
    path('api/admin/users/<int:pk>/', views.AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('api/admin/statistics/', views.AdminStatisticsView.as_view(), name='admin-statistics'),
]
