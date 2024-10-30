from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def companysend_otp_email_task(otp, recipient_email):
    try:
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
        return f'OTP email sent to {recipient_email}'
    except Exception as e:
        return f'Error sending OTP email: {str(e)}'