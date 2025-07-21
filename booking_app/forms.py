from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Booking, Room
import datetime

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['user_name', 'user_email', 'room', 'start_time', 'end_time', 'notes']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        room = cleaned_data.get('room')

        if start_time and end_time:
            if start_time >= end_time:
                raise ValidationError("Час завершення має бути пізніше часу початку")
            
            if start_time < timezone.now():
                raise ValidationError("Не можна бронювати кімнату у минулому")
            
            min_duration = datetime.timedelta(minutes=30)
            if (end_time - start_time) < min_duration:
                raise ValidationError(f"Мінімальна тривалість бронювання - {min_duration}")
            
            max_duration = datetime.timedelta(hours=8)
            if (end_time - start_time) > max_duration:
                raise ValidationError(f"Максимальна тривалість бронювання - {max_duration}")

        if room and start_time and end_time:
            overlapping_bookings = Booking.objects.filter(
                room=room,
                start_time__lt=end_time,
                end_time__gt=start_time,
                status__in=['pending', 'confirmed']
            ).exclude(id=self.instance.id if self.instance else None)
            
            if overlapping_bookings.exists():
                raise ValidationError("Обраний час вже зайнято. Будь ласка, оберіть інший час.")

        return cleaned_data

class RoomAdminForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'