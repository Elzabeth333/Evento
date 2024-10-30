from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from celery.utils.log import get_task_logger
from .email import adminsend_otp_email


logger = get_task_logger(__name__)

@shared_task
def adminsend_otp_email_task(name, email, otp):
    try:
        subject = 'Your OTP Code'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        # Load the HTML template and pass in the context data
        html_content = render_to_string('adminpanel/adminotp_emails.html', {'name': name, 'otp': otp})
        text_content = strip_tags(html_content)  # Fallback for non-HTML email clients

        # Create the email
        msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        
        # Send the email
        msg.send()
        logger.info(f"OTP email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {e}")
        raise






@shared_task
def send_welcome_email(user_email, username):
    subject = "Welcome to Company Panel"
    # Render the HTML template with the context
    html_content = render_to_string('adminpanel/welcome_activated.html', {'username': username})

    # Strip HTML to create the plain text version
    plain_message = strip_tags(html_content)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    # Sending the email
    send_mail(
        subject, 
        plain_message, 
        from_email, 
        recipient_list, 
        html_message=html_content
    )




