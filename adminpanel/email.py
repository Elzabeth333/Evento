from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from datetime import datetime
from django.core.mail import send_mail
from celery.utils.log import get_task_logger
import logging



def adminsend_otp_email(name, email, otp):
    context = {
        'name': name,
        'otp': otp,
    }

    email_subject = 'Your OTP Code'
    email_body = render_to_string('adminpanel/adminotp_emails.html', context)

    email_message = EmailMessage(
        email_subject, email_body,
        settings.DEFAULT_FROM_EMAIL, [email],
    )
    email_message.content_subtype = 'html'  # Set email as HTML
    return email_message.send(fail_silently=False)
