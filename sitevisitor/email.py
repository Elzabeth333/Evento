from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from datetime import datetime
from django.core.mail import send_mail
from celery.utils.log import get_task_logger
import logging


# Create a logger instance
logger = logging.getLogger(__name__)

def site_send_otp_email(name, email, otp):
    context = {
        'name': name,
        'otp': otp,
    }

    email_subject = 'Your OTP Code'
    email_body = render_to_string('sitevisitor/siteotp_emails.html', context)

    email_message = EmailMessage(
        email_subject, email_body,
        settings.DEFAULT_FROM_EMAIL, [email],
    )
    email_message.content_subtype = 'html'  # Set email as HTML
    return email_message.send(fail_silently=False)






def get_welcome_email_content(user_email, first_name):
    subject = "Welcome to Evento!"
    
    # Render the HTML content from a template, passing the first_name as context
    html_message = render_to_string('sitevisitor/welcome_email.html', {'first_name': first_name})
    
    # Optionally, you can set a plain text message
    plain_message = f"Hi {first_name}, welcome to Evento!"
    
    from_email = settings.DEFAULT_FROM_EMAIL
    
    return subject, plain_message, html_message, from_email