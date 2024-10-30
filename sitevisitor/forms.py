from django import forms
from .models import User 
from django.contrib.auth.forms import UserCreationForm 
from django.core.exceptions import ValidationError
import re
from .tasks import send_otp_email_task
import random
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import SetPasswordForm

from adminpanel.models import Attendee, Company ,  Venue,  Message

class AttendeeRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email Address",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label="First Name",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Username"
    )
    password1 = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password"
    )
    password2 = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm Password"
    )
    
   
    class Meta:
        model = User  
        fields = ['first_name',  'email', 'username', 'password1', 'password2']


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username


    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        # Check if password length is at least 8 characters
        if len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        # Check if password contains at least one lowercase letter
        if not re.search(r'[a-z]', password1):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        
        # Check if password contains at least one uppercase letter or number
        if not re.search(r'[A-Z]', password1):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        
        # Check if password contains at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
            raise forms.ValidationError("Password must contain at least one special character.")
                
        # Check if password contains at least one number
        if not re.search(r'[0-9]', password1):
            raise forms.ValidationError("Password must contain at least one number.")
        
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        
        return password2


class AttendeeForm(forms.ModelForm):
    
     class Meta:
        model = Attendee
        fields = ['phone_number', 'profile_image', 'id_proof']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'id_proof': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'attended' : forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={}))
        }

        class Meta:
            model = Attendee
            fields = ['phone_number', 'profile_image', 'id_proof' , 'attended']





class CompanyRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email Address",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label="First Name",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Username"
    )
    password1 = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password"
    )
    password2 = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm Password"
    )
    
   
    class Meta:
        model = User  
        fields = ['first_name',  'email', 'username', 'password1', 'password2']


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username


    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        # Check if password length is at least 8 characters
        if len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        # Check if password contains at least one lowercase letter
        if not re.search(r'[a-z]', password1):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        
        # Check if password contains at least one uppercase letter or number
        if not re.search(r'[A-Z]', password1):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        
        # Check if password contains at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
            raise forms.ValidationError("Password must contain at least one special character.")
                
        # Check if password contains at least one number
        if not re.search(r'[0-9]', password1):
            raise forms.ValidationError("Password must contain at least one number.")
        
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        
        return password2


    


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'phone_number', 
            'profile_image', 
            'id_proof', 
            'id_proof_image', 
            'pan_number', 
            'gst_number'
        ]
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'id_proof': forms.TextInput(attrs={'class': 'form-control'}),
            'id_proof_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'pan_number': forms.TextInput(attrs={'class': 'form-control'}),
            'gst_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if Company.objects.exclude(pk=self.instance.pk).filter(phone_number=phone_number).exists():
            raise forms.ValidationError("This phone number is already registered.")
        return phone_number

    def clean_pan_number(self):
        pan_number = self.cleaned_data.get('pan_number')
        if Company.objects.exclude(pk=self.instance.pk).filter(pan_number=pan_number).exists():
            raise forms.ValidationError("This PAN number is already registered.")
        return pan_number

    def clean_gst_number(self):
        gst_number = self.cleaned_data.get('gst_number')
        if Company.objects.exclude(pk=self.instance.pk).filter(gst_number=gst_number).exists():
            raise forms.ValidationError("This GST number is already registered.")
        return gst_number
    



class AttendeeLoginForm(forms.Form):
    username = forms.CharField(
        max_length=255,
        label="Username",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True  # Ensures the field is mandatory
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password",
        required=True  # Ensures the field is mandatory
    )
    


class CompanyLoginForm(forms.Form):
    username = forms.CharField(
        max_length=255,
        label="Username",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True  # Ensures the field is mandatory
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password",
        required=True  # Ensures the field is mandatory
    )
    




# class EventForm(forms.ModelForm):
#     class Meta:
#         model = Event
#         fields = ['organizer', 'performer', 'title', 'description', 'event_image', 'start_date', 'end_date', 'time', 'location']
#         widgets = {
#             'organizer': forms.Select(attrs={'class': 'form-control'}),
#             'performer' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Performer'}),
#             'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Title'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Event Description'}),
#             'event_image' : forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
#             'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control' , 'type': 'date'}),
#             'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control' , 'type': 'date'}),
#             'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control' , 'type': 'time'}),
#             'location': forms.Select(attrs={'class': 'form-control'}),
#         }






# class TicketForm(forms.ModelForm):
#     class Meta:
#         model = Ticket
#         fields = ['event', 'ticket_type', 'price', 'quantity']
#         widgets = {
#             'event': forms.Select(attrs={'class': 'form-control'}),
#             'ticket_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ticket Type'}),
#             'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price'}),
#             'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'}),
#         }

# class RegistrationForm(forms.ModelForm):
#     class Meta:
#         model = Registration
#         fields = ['user', 'event', 'ticket']
#         widgets = {
#             'user': forms.Select(attrs={'class': 'form-control'}),
#             'event': forms.Select(attrs={'class': 'form-control'}),
#             'ticket': forms.Select(attrs={'class': 'form-control'}),
#         }

class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'location', 'capacity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Venue Name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Venue Location'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Capacity'}),
            
        }

# class ScheduleForm(forms.ModelForm):
#     class Meta:
#         model = Schedule
#         fields = ['event', 'start_time', 'end_time', 'venue', 'stage_no']
#         widgets = {
#             'event': forms.Select(attrs={'class': 'form-control'}),
#             'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
#             'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
#             'venue': forms.Select(attrs={'class': 'form-control'}),
#             'stage_no': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stage Number'}),
#         }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']

    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender', None)
        self.receiver = kwargs.pop('receiver', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        message = super().save(commit=False)
        message.sender = self.sender
        message.receiver = self.receiver
        if commit:
            message.save()
        return message
    




class OTPForms(forms.Form):
    name = forms.CharField(
        max_length=100, 
        error_messages={'required': ''}  # Removes the "This field is required" message
    )
    email = forms.EmailField(
         error_messages={'required': ''} # Removes the "This field is required" message
    )




    def send_otp_email(self):
        otp = random.randint(100000,999999)  # Generate random 4-digit OTP
        send_otp_email_task.delay(
            name=self.cleaned_data['name'],
            email=self.cleaned_data['email'],
            otp=otp
        )
        return otp  # Return OTP for verification




class siteNewPasswordForm(SetPasswordForm):
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
