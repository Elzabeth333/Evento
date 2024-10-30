from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import send_mail
from django.conf import settings
from .email import site_send_otp_email
from .email import get_welcome_email_content
from django.contrib import messages

logger = get_task_logger(__name__)

@shared_task(name="send_otp_email_task", bind=True)
def send_otp_email_task(self, name, email, otp):
    logger.info("Sending OTP email")
    try:
        site_send_otp_email(name=name, email=email, otp=otp)
        return "success", email, otp  # Returning three values
    except Exception as e:
        logger.error(f"Failed to send OTP email: {str(e)}")
        return "failed", str(e), None  # Returning error and None for third value
    
    

@shared_task
def send_welcome_email_task(user_email, first_name):
    subject, plain_message, html_message, from_email = get_welcome_email_content(user_email, first_name)
    
    # Send email using Django's send_mail function
    send_mail(
        subject,  # Subject
        plain_message,  # Plain text version
        from_email,  # From email
        [user_email],  # To email list
        html_message=html_message  # HTML message
    )
    
    # Return a success message for Celery
    return f"Welcome email sent to {user_email}"