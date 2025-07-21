from django.urls import path
from .views import (
    HomeView, 
    RoomDetailView, 
    CreateBookingView, 
    BookingSuccessView,
    BookingListView,
    UpdateBookingStatusView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('room/<int:pk>/', RoomDetailView.as_view(), name='room_detail'),
    path('book/', CreateBookingView.as_view(), name='create_booking'),
    path('booking-success/', BookingSuccessView.as_view(), name='booking_success'),
    path('admin/bookings/', BookingListView.as_view(), name='booking_list'),
    path('admin/bookings/<int:pk>/update/', UpdateBookingStatusView.as_view(), name='update_booking'),
]