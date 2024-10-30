from django import forms
from .models import User 
from .models import  Venue , Message , Profile , Events , BookNoww , TicketType
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import password_validation
from django.contrib.auth.forms import SetPasswordForm
from .tasks import adminsend_otp_email_task
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




class MessageForm(forms.ModelForm):
    to = forms.CharField(max_length=150, help_text="Enter the recipient's username or email.")
    
    class Meta:
        model = Message
        fields = ['to', 'subject', 'body']

    subject = forms.CharField(max_length=255)
    body = forms.CharField(widget=forms.Textarea)


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_image']





class PasswordResetForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Old Password"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="New Password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm New Password"
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Old password is incorrect.")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("The new passwords do not match.")
        
        password_validation.validate_password(new_password1, self.user)
        
        return cleaned_data

    def save(self, commit=True):
        new_password = self.cleaned_data['new_password1']
        self.user.set_password(new_password)
        if commit:
            self.user.save()
        return self.user
    



# forms.py
class adminOTPForm(forms.Form):
    name = forms.CharField(
        label='Name', 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(adminOTPForm, self).__init__(*args, **kwargs)

    def send_otp_email(self):
        if not self.user:
            raise ValueError("User is not available")
        
        if not self.user.email:
            raise ValueError("User email is not available")

        otp = random.randint(100000, 999999)  # Generate random 6-digit OTP
        name = self.cleaned_data.get('name', 'Admin')

        # Log the email address for debugging
        print(f"Sending OTP to: {self.user.email}")

        # Call the Celery task for sending the OTP
        adminsend_otp_email_task.delay(
            name=name,
            email=self.user.email,
            otp=otp
        )
        return otp


class adminNewPasswordForm(SetPasswordForm): 
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