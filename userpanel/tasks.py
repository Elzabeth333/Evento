from celery import shared_task
from celery.utils.log import get_task_logger
from .email import send_otp_email
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib import messages

logger = get_task_logger(__name__)

@shared_task
def send_otp_email_task(name, email, otp):
    try:
        subject = 'Your OTP Code'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        # Load the HTML template and pass in the context data
        html_content = render_to_string('userpanel/otp_emails.html', {'name': name, 'otp': otp})
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









# @shared_task
# def send_otp_email_task(name, email, otp):
#     subject = "Your OTP"
#     message = f"Hello {name}, your OTP is: {otp}"
#     send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])



@shared_task
def send_booking_confirmation_email(user_email, user_name, event_title, ticket_type, number_of_seats, total_price, event_date, booking_serial):
    subject = f"Ticket Booking Confirmation for {event_title}"
    context = {
        'user_name': user_name,
        'event_title': event_title,
        'ticket_type': ticket_type,
        'number_of_seats': number_of_seats,
        'total_price': total_price,
        'event_date': event_date,
        'booking_serial': booking_serial
    }
    html_message = render_to_string('userpanel/ticket_booked_email.html', context)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)




@shared_task
def send_cancellation_email_task(user_email, user_name, event_title, booking_serial, number_of_seats, total_price):
    """
    Sends a ticket cancellation email asynchronously.
    """
    subject = 'Booking Cancellation Confirmation'
    message = f"""
    Dear {user_name},

    Your booking for the event "{event_title}" has been successfully canceled.
    
    Booking Serial: {booking_serial}
    Number of Seats: {number_of_seats}
    Total Refund: ${total_price}

    We hope to see you at future events.

    Best regards,
    Evento Team
    """
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])















































# from celery import shared_task
# from celery.utils.log import get_task_logger
# from django.core.mail import send_mail, EmailMultiAlternatives
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags
# from django.conf import settings

# logger = get_task_logger(__name__)

# @shared_task
# def send_otp_email_task(name, email, otp):
#     try:
#         subject = 'Your OTP Code'
#         from_email = settings.DEFAULT_FROM_EMAIL
#         recipient_list = [email]
#         html_content = render_to_string('userpanel/otp_emails.html', {'name': name, 'otp': otp})
#         text_content = strip_tags(html_content)
        
#         msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
#         msg.attach_alternative(html_content, "text/html")
#         msg.send()
        
#         logger.info(f"OTP email sent to {email}")
#     except Exception as e:
#         logger.error(f"Failed to send OTP email to {email}: {e}")
#         raise

# @shared_task
# def send_booking_confirmation_email(user_email, user_name, event_title, ticket_type, number_of_seats, total_price, event_date, booking_serial):
#     subject = f"Ticket Booking Confirmation for {event_title}"
#     context = {
#         'user_name': user_name,
#         'event_title': event_title,
#         'ticket_type': ticket_type,
#         'number_of_seats': number_of_seats,
#         'total_price': total_price,
#         'event_date': event_date,
#         'booking_serial': booking_serial
#     }
#     html_message = render_to_string('userpanel/ticket_booked_email.html', context)
#     plain_message = strip_tags(html_message)
#     from_email = settings.DEFAULT_FROM_EMAIL
#     recipient_list = [user_email]

#     msg = EmailMultiAlternatives(subject, plain_message, from_email, recipient_list)
#     msg.attach_alternative(html_message, "text/html")
#     msg.send()

# @shared_task
# def send_cancellation_email_task(user_email, user_name, event_title, booking_serial, number_of_seats, total_price):
#     subject = 'Booking Cancellation Confirmation'
#     message = f"""
#     Dear {user_name},

#     Your booking for the event "{event_title}" has been successfully canceled.
    
#     Booking Serial: {booking_serial}
#     Number of Seats: {number_of_seats}
#     Total Refund: ${total_price}

#     We hope to see you at future events.

#     Best regards,
#     Evento Team
#     """
#     send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])

























































