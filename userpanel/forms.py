from django import forms
from adminpanel.models import User , BookNoww ,  Venue
from django.core.exceptions import ValidationError 
from adminpanel.models import User, Company, Attendee, Events
from .models import Blog
from adminpanel.models import Events
from django.contrib.auth.forms import SetPasswordForm
from .tasks import send_otp_email_task
import random


class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'location', 'capacity' , 'venue_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Venue Name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Venue Location'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Capacity'}),
            'venue_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            
        }




class BookNowwForm(forms.ModelForm):
    class Meta:
        model = BookNoww
        fields = ['ticket_type', 'number_of_seats']
        widgets = {
            'ticket_type': forms.Select(attrs={'class': 'form-control'}),
            'number_of_seats': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        self.available_seats = kwargs.pop('available_seats', None)
        super(BookNowwForm, self).__init__(*args, **kwargs)

    def clean_number_of_seats(self):
        number_of_seats = self.cleaned_data.get('number_of_seats')

        if number_of_seats is None:
            raise forms.ValidationError("Please enter a valid number of seats.")

        if self.available_seats is None:
            raise forms.ValidationError("Available seats information is missing.")

        if number_of_seats > self.available_seats:
            raise forms.ValidationError("Number of seats booked cannot exceed available seats.")

        return number_of_seats











   

class BookingForm(forms.Form):
    TICKET_TYPE_CHOICES = [
        ('starter', 'Starter'),
        ('standard', 'Standard'),
        ('platinum', 'Platinum'),
    ]
    
    ticket_type = forms.ChoiceField(choices=TICKET_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    number_of_seats = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))





class OTPForm(forms.Form):
    name = forms.CharField(
        label='Name', 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(OTPForm, self).__init__(*args, **kwargs)

    def send_otp_email(self):
        otp = random.randint(100000, 999999)  # Generate random 6-digit OTP
        if self.user and self.user.email:
            # Call the Celery task for sending the OTP
            send_otp_email_task.delay(
                name=self.cleaned_data['name'],
                email=self.user.email,
                otp=otp
            )
            return otp
        else:
            raise ValueError("User email is not available")












# class OTPForm(forms.Form):
#     name = forms.CharField(
#         label='Name', 
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )

#     def __init__(self, *args, **kwargs):
#         self.user = kwargs.pop('user', None)
#         super(OTPForm, self).__init__(*args, **kwargs)

#     def send_otp_email(self):
#         otp = random.randint(100000, 999999)  # Generate random 6-digit OTP
#         # Ensure the user object is available
#         if self.user and self.user.email:
#             send_otp_email_task.delay(
#                 name=self.cleaned_data['name'],
#                 email=self.user.email,  # Use user's email from the authenticated session
#                 otp=otp
#             )
#             return otp  # Return OTP for session storage
#         else:
#             raise ValueError("User email is not available")
        




class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        label='Enter OTP', 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=6
    )



 

class userNewPasswordForm(SetPasswordForm):
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



    





class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'content', 'image']  # Add any other fields you need
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter blog title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter blog content'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

