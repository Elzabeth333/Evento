from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from adminpanel.models import Events, BookNoww, Venue  # Corrected from DummyBanks to DummyBank
from .forms import BookNowwForm  , OTPVerificationForm , BlogForm , BookingForm
from django.contrib.auth.models import User
from django.db.models import Sum
from .models import Blog
from .forms import userNewPasswordForm 
import uuid
from django.http import HttpResponse
from .forms import OTPForm
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from datetime import datetime, timedelta
from django.core.mail import send_mail
import random
from django.views.generic.edit import FormView
from decimal import Decimal
from django.core.paginator import Paginator
from .tasks import send_booking_confirmation_email , send_cancellation_email_task , send_otp_email_task


# Create your views here.
def user_home(request):
    logged_user = request.user
    today = timezone.now().date()  # Get today's date
    upcoming_events = Events.objects.filter(start_date__gte=today).order_by('start_date')[:8]
    
    # Get the latest event date from the database
    latest_event = Events.objects.order_by('-start_date').first()

    if latest_event:
        latest_event_date = latest_event.start_date
    else:
        latest_event_date = None  # No events exist, handle this scenario gracefully

    if latest_event_date:
        # Calculate the date range for the last 3 days from the latest event date
        two_days_before_latest = latest_event_date - timedelta(days=2)
        
        # Filter events happening in the last 3 days based on the latest event date
        events = Events.objects.filter(start_date__gte=two_days_before_latest, start_date__lte=latest_event_date).order_by('start_date')
        
        # Group events by day
        events_by_day = {
            'Day01': events.filter(start_date=latest_event_date),
            'Day02': events.filter(start_date=latest_event_date - timedelta(days=1)),
            'Day03': events.filter(start_date=latest_event_date - timedelta(days=2)),
        }
    else:
        # If no events are found, create an empty dictionary
        events_by_day = {}

    blogs = Blog.objects.all().order_by('-created_at')[:3]

    context = {
        'upcoming_events': upcoming_events,
        'events_by_day': events_by_day,
        'events' : events ,
        'blogs' : blogs
}


    return render(request, 'userpanel/user_home.html', context)  





def event_details(request, event_id):
    # Fetch the event by its ID
    event = get_object_or_404(Events, id=event_id)
    standard_price = event.ticket_price * 2
    platinum_price = event.ticket_price * 3
    
    # Context to pass to the template
    context = {
        'event': event,
        'venue': event.location , # Assuming 'location' is the ForeignKey to Venue
        'standard_price' : standard_price,
        'platinum_price' : platinum_price
    }
    
    return render(request, 'userpanel/event_details.html', context)





def completed_event_details(request, event_id):
    # Fetch the event by its ID
    event = get_object_or_404(Events, id=event_id)

   # Check if the event was completed by yesterday
    if event.end_date <= (timezone.now() - timezone.timedelta(days=1)).date():
        context = {
            'event': event,
        }
    else:
        context = {
            'error': 'This event has not been completed yet.'
        }
    return render(request, 'userpanel/completed_eventdetail.html', context)




def book_now_vieww(request, event_id):
    event = get_object_or_404(Events, id=event_id)
    bookings = BookNoww.objects.filter(event=event)

    if request.method == 'POST':
        form = BookNowwForm(request.POST, available_seats=event.seats_available)
        if form.is_valid():
            # Saving the form should handle the creation of a booking record
            new_booking = form.save(commit=False)
            new_booking.event = event
            new_booking.save()
            return redirect('compare_bank', event_id=event_id)  # Assuming 'compare_bank' is your intended redirect.
    else:
        form = BookNowwForm(available_seats=event.seats_available)

    context = {
        'form': form,
        'event': event,
        'available_seats': event.seats_available,
        'bookings': bookings,
    }

    return render(request, 'userpanel/book_now.html', context)



def booking_form(request, event_id):
    event = get_object_or_404(Events, id=event_id)
    form = BookingForm(request.POST or None)

    total_price = None
    booking_details = request.session.get('booking_details', None)

    if request.method == 'POST' and form.is_valid():
        ticket_type = form.cleaned_data.get('ticket_type')
        number_of_seats = form.cleaned_data.get('number_of_seats')
        base_price = event.ticket_price

        # Calculate the total price
        if ticket_type == 'starter':
            total_price = base_price * number_of_seats
        elif ticket_type == 'standard':
            total_price = base_price * 2 * number_of_seats
        elif ticket_type == 'platinum':
            total_price = base_price * 3 * number_of_seats

        # Store booking details and event_id in session
        booking_data = form.cleaned_data
        booking_data['event_id'] = event.id
        request.session['booking_details'] = booking_data
        request.session['total_price'] = float(total_price)
        request.session['event_id'] = event.id  # Store the event_id for future use

        return redirect('request_otp')

    total_price = request.session.get('total_price', None)
    bookings = BookNoww.objects.filter(event=event)

    return render(request, 'userpanel/booking_form.html', {
        'form': form,
        'event': event,
        'total_price': total_price,
        'booking_details': booking_details,
        'bookings': bookings,
    })






@login_required  # Ensures that the user must be logged in
def request_otp(request):
    if request.method == 'POST':
        form = OTPForm(request.POST, user=request.user)  # Pass the user to the form
        if form.is_valid():
            otp = form.send_otp_email()  # This internally calls the Celery task
            request.session['otp'] = otp
            messages.success(request, "OTP has been sent to your email.")
            return redirect('verify_otp')
    else:
        form = OTPForm()

    return render(request, 'userpanel/otp_request.html', {'form': form})








def verify_otp(request):
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            if otp == str(request.session.get('otp')):
                booking_details = request.session.get('booking_details')
                if booking_details:
                    event_id = booking_details['event_id']
                    number_of_seats = booking_details['number_of_seats']
                    ticket_type = booking_details['ticket_type']
                    event = get_object_or_404(Events, id=event_id)

                    if event.reduce_seats(number_of_seats):  # Ensure this function locks the row for update
                        base_price = event.ticket_price
                        multiplier = {'starter': 1, 'standard': 2, 'platinum': 3}.get(ticket_type, 1)
                        total_price = base_price * number_of_seats * multiplier

                        new_booking = BookNoww.objects.create(
                            user=request.user,
                            event=event,
                            ticket_type=ticket_type,
                            number_of_seats=number_of_seats,
                            available_seats=event.seats_available,
                            ticket_price=total_price
                        )

                        send_booking_confirmation_email.delay(
                            user_email=request.user.email,
                            user_name=request.user.get_full_name(),
                            event_title=event.title,
                            ticket_type=ticket_type,
                            number_of_seats=number_of_seats,
                            total_price=total_price,
                            event_date=event.start_date,
                            booking_serial=new_booking.booking_serial  # Corrected to use the new booking instance
                        )

                        del request.session['otp']
                        del request.session['booking_details']
                        del request.session['total_price']
                        messages.success(request, 'Tickets booked successfully!')
                        return redirect('booking_confirmation')
                    else:
                        messages.error(request, 'Not enough seats available.')
                else:
                    messages.error(request, 'Booking details not found.')
            else:
                messages.error(request, 'Invalid OTP.')
    else:
        form = OTPVerificationForm()

    return render(request, 'userpanel/otp_verification.html', {'form': form})



def booking_confirmation(request):
    # Get the event_id from the session or request
    event_id = request.session.get('event_id', None) or request.GET.get('event_id', None)

    if not event_id:
        messages.error(request, "Event ID is missing.")
        return redirect('booking_form', event_id=event_id)  # Fallback view if no event_id is found

    event = get_object_or_404(Events, id=event_id)

    booking_details = request.session.get('booking_details')
    if not booking_details:
        messages.error(request, "No booking details found.")
        return redirect('booking_form', event_id=event_id)

    booking = BookNoww.objects.filter(
        event=event,
        ticket_type=booking_details['ticket_type'],
        number_of_seats=booking_details['number_of_seats']
    ).last()

    if booking is None:
        messages.error(request, "Booking record not found.")
        return redirect('booking_form', event_id=event_id)

    return render(request, 'userpanel/booking_confirmation.html', {
        'event': event,
        'details': booking_details,
        'total_price': request.session.get('total_price', 'Not available'),
        'booking': booking
    })






def cancel_booking(request, booking_id):
    booking = get_object_or_404(BookNoww, id=booking_id)

    if request.method == 'POST':
        # Store necessary details for sending the email before deleting the booking
        booking_serial = booking.booking_serial
        event_title = booking.event.title
        event_id = booking.event.id  # Store the event_id before deleting the booking
        number_of_seats = booking.number_of_seats
        ticket_type = booking.ticket_type  # Corrected to use the model field directly
        event = get_object_or_404(Events, id=event_id)
        base_price = event.ticket_price
        multiplier = {'starter': 1, 'standard': 2, 'platinum': 3}.get(ticket_type, 1)
        total_price = base_price * number_of_seats * multiplier
        user_email = booking.user.email
        user_name = booking.user.get_full_name()

        # Delete the booking
        booking.delete()

        # Send cancellation email asynchronously
        send_cancellation_email_task.delay(
            user_email=user_email,
            user_name=user_name,
            event_title=event_title,
            booking_serial=booking_serial,
            number_of_seats=number_of_seats,
            total_price=total_price
        )

        messages.success(request, 'Your booking has been successfully canceled.')
        return redirect('booking_form', event_id=event_id)  # Pass the event_id in the redirect
    
    return render(request, 'userpanel/cancellation_confirmation.html', {'booking': booking})



    

# Blog listing view
def blog_list(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'userpanel/blog_list.html', {'blogs': blogs})

# Blog creation view
@login_required
def add_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            return redirect('blog_list')
    else:
        form = BlogForm()
    
    return render(request, 'userpanel/add_blog.html', {'form': form})


def user_about(request):
    return render(request, 'userpanel/user_about.html')


def user_event_list(request):
    today = timezone.now().date()  # Get today's date
    upcoming_events = Events.objects.filter(start_date__gte=today)  # Events starting today or later

    return render(request, 'userpanel/user_event_list.html', {
        'upcoming_events': upcoming_events,
    })



# View for all events (with optional pagination)
def all_events_view(request):
    today = timezone.now().date()
    all_events = Events.objects.filter(start_date__gte=today).order_by('start_date')

    # Pagination (optional)
    paginator = Paginator(all_events, 8)  # Show 8 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'userpanel/all_events.html', {'page_obj': page_obj})



def blog_detail_view(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    return render(request, 'userpanel/blog_detail.html', {'blog': blog})



@login_required
def blog_edit_view(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id, author=request.user)  # Only allow authors to edit their own blogs
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('blog_detail', blog_id=blog.id)
    else:
        form = BlogForm(instance=blog)
    return render(request, 'userpanel/blog_edit.html', {'form': form, 'blog': blog})



@login_required
def blog_delete_view(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id, author=request.user)  # Only allow authors to delete their own blogs
    if request.method == 'POST':
        blog.delete()
        return redirect('all_blogs')
    return render(request, 'userpanel/blog_delete.html', {'blog': blog})


def completed_events(request):
    today = timezone.now().date()  # Get today's date
    completed_events = Events.objects.filter(end_date__lt=today)  # Filter events that have ended
    return render(request, 'userpanel/usercompleted_events.html', {'completed_events': completed_events})





def userreset_password(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, 'User does not exist.')
        return redirect('attendee_login')

    if request.method == 'POST':
        form = userNewPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been reset successfully!')
            return redirect('attendee_login')
    else:
        form = userNewPasswordForm(user)

    return render(request, 'userpanel/userreset_password.html', {'form': form, 'username': username})



# View to log out the user
def user_logout(request):
    logout(request)  # Log out the user
    return redirect('home')


