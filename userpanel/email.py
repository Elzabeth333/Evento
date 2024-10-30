from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from datetime import datetime
from django.core.mail import send_mail
from celery.utils.log import get_task_logger
import logging

logger = logging.getLogger(__name__)

def send_otp_email(name, email, otp):
    context = {
        'name': name,
        'otp': otp,
    }

    email_subject = 'Your OTP Code'
    email_body = render_to_string('userpanel/otp_emails.html', context)

    email_message = EmailMessage(
        email_subject, email_body,
        settings.DEFAULT_FROM_EMAIL, [email],
    )
    email_message.content_subtype = 'html'  # Set email as HTML
    try:
        email_message.send(fail_silently=False)
        logger.info(f"OTP email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {e}")
        raise




def send_booking_confirmation_email(user_email, user_name, event_title, ticket_type, number_of_seats, total_price, event_date):
    subject = f"Ticket Booking Successful for {event_title}"
    html_message = render_to_string('userpanel/ticket_booked_email.html', {
        'user_name': user_name,
        'event_title': event_title,
        'ticket_type': ticket_type,
        'number_of_seats': number_of_seats,
        'total_price': total_price,
        'event_date': event_date
    })
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)





def send_cancellation_email(user, event, ticket_type, number_of_seats, total_refund):
    """
    Sends a ticket cancellation email to the user.
    """
    subject = f"Your Ticket for {event.title} Has Been Cancelled"
    
    # Render the HTML email template with the cancellation details
    html_message = render_to_string('userpanel/ticket_cancellation_email.html', {
        'user_name': user.first_name,
        'event_title': event.title,
        'ticket_type': ticket_type,
        'number_of_seats': number_of_seats,
        'total_refund': total_refund,
    })
    
    # Create a plain-text version of the message
    plain_message = strip_tags(html_message)
    
    # Sender email
    from_email = settings.DEFAULT_FROM_EMAIL
    
    # Recipient list (only one recipient in this case)
    recipient_list = [user.email]
    
    # Send the email
    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)