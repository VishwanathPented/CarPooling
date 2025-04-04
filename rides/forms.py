from django import forms
from .models import Ride, RideRequest, Rating

class RideForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = ['start_point', 'end_point', 'departure_time', 'seats_available']
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'comment']