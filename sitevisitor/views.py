from django.contrib.auth.models import Group , User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from adminpanel.models import Notification
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.views.generic.edit import FormView
from django.http import HttpResponse
from .forms import OTPForms , siteNewPasswordForm
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login
from .tasks import send_otp_email_task ,  send_welcome_email_task
from .forms import CompanyRegistrationForm, CompanyForm, MessageForm , CompanyLoginForm
from adminpanel.models import Notification , Company 
from .forms import AttendeeRegistrationForm , AttendeeLoginForm , AttendeeForm ,  CompanyRegistrationForm , CompanyForm
from django.shortcuts import render
from userpanel.models import  Blog
from adminpanel.models import Events



# Create your views here.
def home(request):
    latest_events = Events.objects.all().order_by('-start_date')[:5]  # Fetch the latest 5 events
    companies = Company.objects.filter(is_active=True)  # Get active companies
    blogs = Blog.objects.all().order_by('-created_at')[:2]
    return render(request, 'sitevisitor/home.html' , {'latest_events' : latest_events , 'companies' : companies , 'blogs': blogs})


def register_attendee(request):
    if request.method == 'POST':
        form = AttendeeRegistrationForm(request.POST)
        form1 = AttendeeForm(request.POST , request.FILES)
        if form.is_valid() and form1.is_valid():
            user = form.save()
            attendee = form1.save(commit=False)
            attendee.user = user
            attendee.save()

            # Get user email and first name
            user_email = user.email
            first_name = user.first_name
            
            # Call the Celery task to send the email asynchronously
            send_welcome_email_task.delay(user_email, first_name)

            # Success message
            messages.success(request, f'User {user.first_name} registered successfully! A welcome email has been sent to {user.email}.')
            return redirect('attendee_login')  # Redirect to login page
    
    else:
        form = AttendeeRegistrationForm()
        form1 = AttendeeForm()

    return render(request, 'sitevisitor/register_attendee.html',{'form':form , 'form1': form1})




def Attendee_Login(request):
    if request.method == 'POST':
        form = AttendeeLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('user_home')  # Redirect to a success page
            else:
                form.add_error(None, 'Invalid username or password')  # Add a non-field error
    else:
        form = AttendeeLoginForm()  # Create an empty form for GET requests

    return render(request, 'sitevisitor/login_attendee.html', {'form': form})



def register_company(request):
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)
        form1 = CompanyForm(request.POST, request.FILES)
        if form.is_valid() and form1.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.is_active = False  # Initially set the user as inactive
            user.save()
            
            company = form1.save(commit=False)
            company.user = user
            company.is_active = False  # Initially set the company as inactive
            company.save()
            
            # Ensure the 'Manager' group exists
            manager_group, created = Group.objects.get_or_create(name='Manager')
            user.groups.add(manager_group)  # Assign the user to the 'Manager' group

            # Send a message to the first admin
            admin_users = User.objects.filter(is_staff=True)
            if admin_users.exists():
                receiver = admin_users[0]  # Get the first admin user
                message_form = MessageForm({
                    'subject': 'New Company Registration',
                    'body': f'A new company manager ({user.username}) has registered and is awaiting approval.',
                }, sender=user, receiver=receiver)

                if message_form.is_valid():
                    message_form.save()

            # Create a notification for all superusers
            admins = User.objects.filter(is_superuser=True)
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    message=f'New company manager registered: {user.username}. Please review and activate.'
                )

            messages.success(request, 'Manager registered successfully. Awaiting admin approval.')
            return redirect('company_login')
    else:
        form = CompanyRegistrationForm()
        form1 = CompanyForm()

    return render(request, 'sitevisitor/register_company.html', {'form': form, 'form1': form1})



# def register_company(request):
#     if request.method == 'POST':
#         form = CompanyRegistrationForm(request.POST)
#         form1 = CompanyForm(request.POST, request.FILES)
#         if form.is_valid() and form1.is_valid():
#             user = form.save(commit=False)
#             user.is_staff = True
#             user.is_active = False  # Initially set the user as inactive
#             user.save()
            
#             company = form1.save(commit=False)
#             company.user = user
#             company.is_active = False  # Initially set the company as inactive
#             company.save()
            
#             # Ensure the 'Manager' group exists
#             manager_group, created = Group.objects.get_or_create(name='Manager')

#             # Assign the user to the 'Manager' group
#             user.groups.add(manager_group)

#             # Create a notification for all admins
#             admins = User.objects.filter(is_superuser=True)
#             for admin in admins:
#                 Notification.objects.create(
#                     user=admin,
#                     message=f'New company manager registered: {user.username}. Please review and activate.'
#                 )

#                 # Send email notification to admin
#                 subject = 'New Company Registration'
#                 html_message = render_to_string('adminpanel/admin_mailbox.html', {
#                     'username': user.username,
#                     'email': user.email,
#                     'phone_number': company.phone_number,
#                     'registration_date': company.created_at,
#                 })
#                 plain_message = strip_tags(html_message)
#                 send_mail(subject, plain_message, 'your-email@example.com', [admin.email], html_message=html_message)

#             messages.success(request, 'Manager registered successfully. Awaiting admin approval.')
#             return redirect('company_login')
#     else:
#         form = CompanyRegistrationForm()
#         form1 = CompanyForm()

#     return render(request, 'sitevisitor/register_company.html', {'form': form, 'form1': form1})



def company_login(request):
    if request.method == 'POST':
        form = CompanyLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.groups.filter(name='Manager').exists():  # Check if the user is in the "Manager" group
                    if user.is_active:  # Check if the user account is active
                        login(request, user)
                        return redirect('company_home')
                    else:
                        # Display error if the user is inactive (deleted)
                        messages.error(request, 'Your account has been deleted by the admin.')
                else:
                    messages.error(request, 'You do not have permission to access this area.')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = CompanyLoginForm()

    return render(request, 'sitevisitor/login_company.html', {'form': form})



def admin_login(request):
    
    if request.method == 'POST':
        form = AttendeeLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            print(password)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                
                if  user.is_staff:                  
                                       
                    return redirect('admin_home')    
                         
            else:                
                messages.error(request, 'Invalid username or password')
    else:
        form = AttendeeLoginForm()
    return render(request, 'sitevisitor/admin_login.html', {'form': form})


def custom_404_view(request):
    return render(request, 'sitevisitor/404.html')
    


class OTPRequestViews(FormView):
    template_name = 'sitevisitor/siteotp_form.html'
    form_class = OTPForms

    def form_valid(self, form):
        otp = form.send_otp_email()
        self.request.session['otp'] = otp
        self.request.session['username'] = form.cleaned_data['name']  # Store username in session
        return redirect(reverse('sitevisitor_verifyotpviews'))



def sitevisitor_verifyotpviews(request):
    if request.method == "POST":
        input_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        username = request.session.get('username')  # Get username from session
        
        if not username:
            return HttpResponse("Username not found in session.", status=400)

        if input_otp == str(session_otp):
            # OTP is verified, redirect to reset password page
            return redirect(reverse('sitevisitor_resetpassword', kwargs={'username': username}))
        else:
            return HttpResponse("Invalid OTP. Please try again.")
    
    return render(request, 'sitevisitor/sitevisitor_verifyotpviews.html')




def sitevisitor_resetpassword(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, 'User does not exist.')
        return redirect('attendee_login')

    if request.method == 'POST':
        form = siteNewPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been reset successfully!')
            return redirect('attendee_login')
    else:
        form = siteNewPasswordForm(user)

    return render(request, 'sitevisitor/sitevisitor_resetpassword.html', {'form': form, 'username': username})



def siteforgot_password(request):
    return render(request,'sitevisitor/siteforgot_password.html')


