from django import forms
from  adminpanel.models import User 
from django.contrib.auth.forms import UserCreationForm
from adminpanel.models import Attendee, Company , Venue , Events
from .tasks import companysend_otp_email_task  # Import your Celery task
import random
from django.contrib.auth.forms import SetPasswordForm
from .tasks import companysend_otp_email_task
import random





class EventForm(forms.ModelForm):
    class Meta:
        model = Events
        fields = ['organizer', 'title', 'description', 'event_image', 'start_date', 'end_date', 'time', 'location', 'ticket_price']
        widgets = {
            'organizer': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Event Description'}),
            'event_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'ticket_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ticket Price'}),
        }
        
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        # Filter users to include only those who are staff and not superusers
        self.fields['organizer'].queryset = User.objects.filter(is_staff=True, is_superuser=False)





class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'location', 'capacity', 'venue_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Venue Name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Venue Location'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Capacity'}),
            'venue_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }



class companyOTPForm(forms.Form):
    name = forms.CharField(max_length=150)
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(companyOTPForm, self).__init__(*args, **kwargs)

    def generate_otp(self):
        """Generate a 6-digit OTP"""
        return random.randint(100000, 999999)

    def send_otp_email(self):
        """Send the OTP via email using Celery task"""
        otp = self.generate_otp()
        recipient_email = self.cleaned_data['email']
        companysend_otp_email_task.delay(otp, recipient_email)  # Use Celery to send email
        return otp




class companyNewPasswordForm(SetPasswordForm): 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    new_password1 = forms.CharField(
        label="New Password", 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    new_password2 = forms.CharField(
        label="Confirm New Password", 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )