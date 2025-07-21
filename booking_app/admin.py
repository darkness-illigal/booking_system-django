from django.contrib import admin
from .models import Room, Booking, RoomFeature
from .forms import RoomAdminForm

@admin.register(RoomFeature)
class RoomFeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    form = RoomAdminForm
    list_display = ('name', 'capacity', 'price_per_hour', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    filter_horizontal = ('features',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'user_name', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'room')
    search_fields = ('user_name', 'user_email', 'room__name')
    date_hierarchy = 'start_time'
    actions = ['confirm_bookings', 'cancel_bookings']

    def confirm_bookings(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, f"{queryset.count()} бронювань підтверджено")
    confirm_bookings.short_description = "Підтвердити вибрані бронювання"

    def cancel_bookings(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"{queryset.count()} бронювань скасовано")
    cancel_bookings.short_description = "Скасувати вибрані бронювання"