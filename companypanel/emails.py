from django.core.mail import send_mail
from django.conf import settings

def send_otp_email(otp, recipient_email):
    """Send OTP email to the user"""
    subject = 'Your OTP Code'
    message = f'Your OTP is {otp}. Please use this to verify your identity.'
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(
        subject,
        message,
        from_email,
        [recipient_email],
        fail_silently=False
    )
