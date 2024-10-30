from django.urls import  path
from .views import home , Attendee_Login , OTPRequestViews, sitevisitor_verifyotpviews , siteforgot_password , sitevisitor_resetpassword , register_attendee , custom_404_view ,  company_login , register_company , admin_login

urlpatterns = [
    path('', home , name='home'),
    path('siteforgot_password/', siteforgot_password , name ='siteforgot_password'),
    path('attendee/', Attendee_Login , name='attendee_login'),
    path('register_attendee/', register_attendee , name='register_attendee'),
    path('company_login/', company_login , name='company_login'),
    path('register_company/', register_company , name='register_company'),
    path('admin_login/', admin_login , name='admin_login'),
    path('404/' , custom_404_view , name='custom_404_view' ),
    path('siterequest-otp/', OTPRequestViews.as_view(), name='siterequest_otp'),
    path('sitevisitor_verifyotpviews/', sitevisitor_verifyotpviews, name='sitevisitor_verifyotpviews'),
    path('sitevisitor_resetpassword/<str:username>/', sitevisitor_resetpassword, name='sitevisitor_resetpassword'),
]