from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Room, Booking, RoomFeature
from .forms import BookingForm, RoomAdminForm
import datetime

class HomeView(View):
    def get(self, request):
        rooms = Room.objects.filter(is_active=True)
        return render(request, 'booking_app/home.html', {'rooms': rooms})

class RoomDetailView(DetailView):
    model = Room
    template_name = 'booking_app/room_detail.html'
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BookingForm(initial={'room': self.object})
        return context

class CreateBookingView(CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'booking_app/create_booking.html'
    success_url = reverse_lazy('booking_success')

    def form_valid(self, form):
        response = super().form_valid(form)
        
        subject = f"Підтвердження бронювання #{self.object.id}"
        message = (
            f"Дякуємо за ваше бронювання, {self.object.user_name}!\n\n"
            f"Деталі бронювання:\n"
            f"Кімната: {self.object.room.name}\n"
            f"Дата та час: {self.object.start_time.strftime('%d.%m.%Y %H:%M')} - {self.object.end_time.strftime('%H:%M')}\n"
            f"Статус: {self.object.get_status_display()}\n\n"
            f"Код підтвердження: {self.object.confirmation_code}\n\n"
            "Якщо ви не робили це бронювання, будь ласка, повідомте нас."
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.object.user_email],
            fail_silently=False,
        )
        
        messages.success(self.request, "Бронювання успішно створено! На вашу пошту відправлено підтвердження.")
        return response

class BookingSuccessView(View):
    def get(self, request):
        return render(request, 'booking_app/booking_success.html')

class BookingListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Booking
    template_name = 'booking_app/admin/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        queryset = super().get_queryset()
        
        status = self.request.GET.get('status')
        if status in ['pending', 'confirmed', 'cancelled']:
            queryset = queryset.filter(status=status)
        
        room_id = self.request.GET.get('room_id')
        if room_id:
            queryset = queryset.filter(room_id=room_id)
        
        date = self.request.GET.get('date')
        if date:
            try:
                date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
                queryset = queryset.filter(
                    start_time__date=date_obj
                )
            except ValueError:
                pass
        
        return queryset.order_by('-start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rooms'] = Room.objects.all()
        return context

class UpdateBookingStatusView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Booking
    fields = ['status']
    template_name = 'booking_app/admin/update_booking.html'
    success_url = reverse_lazy('booking_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Статус бронювання #{self.object.id} оновлено до {self.object.get_status_display()}")
        return response