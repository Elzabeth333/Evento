from django.shortcuts import render , redirect
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from adminpanel.models import Message , Company , Attendee , Venue , Events , BookNoww
from userpanel.models import Blog
from django.contrib import messages
from django.utils import timezone  # Import timezone to set the current time
from sitevisitor.forms import MessageForm 
from .forms import VenueForm , EventForm , companyOTPForm, companyNewPasswordForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models import OuterRef, Subquery
from django.urls import reverse
from django.views.generic.edit import FormView
from django.contrib import messages
from django.http import HttpResponse





# Create your views here.
@login_required(login_url='/404/')
def company_home(request, user_id=None):
    logged_user = request.user
    events = Events.objects.all()[:4]
    events_all = Events.objects.all()

    # Handle sending a new message
    if request.method == 'POST':
        message_text = request.POST.get('message')
        receiver_id = request.POST.get('receiver_id')

        # Check if receiver_id is provided and valid
        if receiver_id:
            try:
                receiver = get_object_or_404(User, id=int(receiver_id))
            except ValueError:
                receiver = None
        else:
            receiver = None

        if message_text and receiver:
            # Create a new message
            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                body=message_text
            )

        # Redirect back to the chat page with the receiver
        if receiver:
            return redirect('manager_chat', user_id=receiver.id)

    # Get all users who are part of the manager group, are staff, and not superusers
    admin_users = User.objects.filter(
        is_superuser=True,
        is_staff=True,
    ).select_related('profile')

    # Subquery to get the latest message for each manager
    latest_message_subquery = Message.objects.filter(
        sender=OuterRef('pk')
    ).order_by('-created_at').values('subject', 'created_at')[:1]

    selected_user = None
    messages = None

    # Automatically select the most recent user conversation if none is selected
    if not user_id:
        last_conversation = Message.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user)
        ).order_by('-created_at').first()
        if last_conversation:
            if last_conversation.sender == request.user:
                user_id = last_conversation.receiver.id
            else:
                user_id = last_conversation.sender.id

    if user_id:
        # Get the selected user
        selected_user = get_object_or_404(User, id=user_id)

        # Fetch all messages between the logged-in admin and the selected user
        messages = Message.objects.filter(
            sender__in=[request.user, selected_user],
            receiver__in=[request.user, selected_user],
            is_deleted=False
        ).order_by('created_at')

    # Get all users who are part of the manager group, are staff, and not superusers
    chat_admin_users = User.objects.filter(
        is_superuser=True,
        is_staff=True,
    ).select_related('company').annotate(
        last_message_subject=Subquery(latest_message_subquery.values('subject')[:1]),
        last_message_date=Subquery(latest_message_subquery.values('created_at')[:1])
    )

    company = get_object_or_404(Company, user=logged_user)
    company_notifications = Message.objects.filter(sender__is_active=False, is_deleted=False).order_by('-created_at')
    company_notification_count = company_notifications.count()

    sent_messages = Message.objects.filter(sender=request.user)
    received_messages = Message.objects.filter(receiver=request.user)

    user_ids = set(sent_messages.values_list('receiver_id', flat=True)) | set(received_messages.values_list('sender_id', flat=True))

    company_users = User.objects.filter(id__in=user_ids).exclude(id=request.user.id)

    user_unread_counts = {
        user.id: Message.objects.filter(sender=user, receiver=request.user, is_read=False, is_deleted=False).count()
        for user in company_users
    }

    company_message_notifications = Message.objects.filter(receiver=request.user, is_read=False, is_deleted=False, sender__is_active=True).order_by('-created_at')[:5]
    company_message_notifications_count = company_message_notifications.count()

    admin_users = User.objects.filter(is_superuser=True).select_related('profile')

    venues_list = Venue.objects.all()

    total_events = Events.objects.count()

    # Total tickets booked
    total_tickets_booked = BookNoww.objects.aggregate(total_tickets=Sum('number_of_seats'))['total_tickets'] or 0

    # Total amount received
    total_amount_received = BookNoww.objects.aggregate(total_amount=Sum('ticket_price'))['total_amount'] or 0.0

    # Event with the most tickets booked
    top_event = (
        BookNoww.objects.values('event__title')
        .annotate(total_tickets=Sum('number_of_seats'))
        .order_by('-total_tickets')
        .first()
    )


    # Total blogs
    total_blogs = Blog.objects.count()

    # Total users (excluding staff)
    total_users = User.objects.filter(is_staff=False).count()

    # Completed events (events with an end date before today)
    completed_events = Events.objects.filter(end_date__lt=timezone.now()).count()

    # Upcoming events (events with a start date greater than or equal to today)
    upcoming_events = Events.objects.filter(start_date__gte=timezone.now()).count()

    upcoming_eventss = Events.objects.filter(start_date__gte=timezone.now())

    context = {
        'logged_user': logged_user,
        'venues_list' : venues_list ,
        'admin_users': admin_users,
        'events_all' : events_all ,
        'events' : events ,
        'chat_admin_users': chat_admin_users,
        'selected_user': selected_user,
        'messages': messages,
        'company_notifications': company_notifications,
        'company_notification_count': company_notification_count,
        'company_users': company_users,
        'user_unread_counts': user_unread_counts,
        'company_message_notifications': company_message_notifications,
        'company_message_notifications_count': company_message_notifications_count,
        'total_events': total_events,
        'total_tickets_booked': total_tickets_booked,
        'total_amount_received': total_amount_received,
        'top_event': top_event,
        'total_blogs': total_blogs,
        'total_users': total_users,
        'completed_events': completed_events,
        'upcoming_events': upcoming_events,
        'upcoming_eventss': upcoming_eventss

    }

    return render(request, 'companypanel/company_home.html', context)



@login_required(login_url='/404/')
def company_inbox(request):
    logged_user = request.user
    print("Inbox view accessed")  # Debugging statement
    messages = Message.objects.filter(receiver=request.user).order_by('-created_at')
    context = {'messages': messages , 'logged_user' : logged_user }
    return render(request, 'companypanel/company_inbox.html', context)


@login_required(login_url='/404/')
def message_detail(request, message_id):
    logged_user = request.user
    message = get_object_or_404(Message, id=message_id, receiver=request.user)
    
    if not message.is_read:  # Check if the message is not already read
        message.is_read = True  # Mark as read
        message.save()  # Save the change to the database
    
    return render(request, 'companypanel/company_message_detail.html', {'message': message, 'logged_user': logged_user})



@login_required(login_url='/404/')
def company_compose_message(request):
    logged_user = request.user
    messages_inbox = Message.objects.filter(receiver=request.user).order_by('-created_at')
    reply_to = request.GET.get('reply')
    if reply_to:
        original_message = get_object_or_404(Message, id=reply_to)
        form = MessageForm(initial={
            'recipient': original_message.sender,  # Assuming 'recipient' is a field in your MessageForm
            'subject': f"Re: {original_message.subject}"
        })
    else:
        form = MessageForm()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            
            # Check if it's a reply
            if reply_to:
                message.receiver = original_message.sender  # Set receiver to the sender of the original message
            
            # Ensure receiver is set if not a reply
            if not message.receiver:
                messages.error(request, 'Receiver is required.')
                return render(request, 'companypanel/company_compose_message.html', {'form': form})

            message.save()
            messages.success(request, 'Message sent successfully.')
            return redirect('company_inbox')
        else:
            messages.error(request, 'There was an error in your form. Please correct it.')
    

    return render(request, 'companypanel/company_compose_message.html', {'form': form , 'messages_inbox': messages_inbox , 'logged_user': logged_user})




@login_required(login_url='/404/')
def new_compose(request):
    logged_user = request.user
    admin_users = User.objects.filter(is_staff=True)
    # receiver = get_object_or_404(User, id=receiver_id)
    receiver = admin_users[0]
    if request.method == 'POST':
        form = MessageForm(request.POST, sender=request.user, receiver=receiver)
        if form.is_valid():
            form.save()
            
            return redirect('company_inbox')
    else:
        form = MessageForm(sender=request.user, receiver=receiver)
    
    return render(request, 'companypanel/new_compose.html', {'form': form, 'receiver': receiver , 'logged_user' : logged_user , 'admin_users' : admin_users})



@login_required(login_url='/404/')
def company_sent_items(request):
    logged_user = request.user
    sent_messages = Message.objects.filter(sender=request.user, is_deleted=False).order_by('-created_at')
    return render(request, 'companypanel/company_sent_items.html', {'sent_messages': sent_messages ,  'logged_user': logged_user})



@login_required(login_url='/404/')
def company_sent_details(request, message_id):
    logged_user = request.user
    # Try to get the message where the user is either the sender or the receiver
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    return render(request, 'companypanel/company_sent_details.html', {'message': message ,  'logged_user': logged_user})


@login_required(login_url='/404/')
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    if request.method == 'POST':
        message.is_deleted = True  # Mark the message as deleted
        message.deleted_at = timezone.now()  # Set the deleted_at field to the current time
        message.save()  # Save the change to the database  # Save the change to the database
        return redirect('company_sent_items')  # Redirect to the sent items page
    return redirect('company_sent_items')


@login_required(login_url='/404/')
def deleted_messages_view(request):
    logged_user = request.user
    # Filter messages that are marked as deleted and where the logged-in user is either the sender or receiver
    deleted_messages = Message.objects.filter(is_deleted=True).filter(
        Q(sender=logged_user) | Q(receiver=logged_user)
    )
    return render(request, 'companypanel/deleted_messages.html', {'deleted_messages': deleted_messages, 'logged_user': logged_user})



@login_required(login_url='/404/')
def venue_list(request):
    logged_user = request.user
    query = request.GET.get('table_search')
    if query:
        venues = Venue.objects.filter(
            Q(name__icontains=query) | 
            Q(location__icontains=query) |
            Q(capacity__icontains=query)
        )
    else:
        venues = Venue.objects.all()

    return render(request, 'companypanel/venue_list.html', {'venues': venues , 'logged_user':logged_user})



@login_required(login_url='/404/')
def add_venue(request):
    logged_user = request.user
    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('venue_list')
    else:
        form = VenueForm()
    return render(request, 'companypanel/add_venue.html', {'form': form , 'logged_user':logged_user})


@login_required(login_url='/404/')
def add_event(request):
    logged_user = request.user
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid() :
            form.save()
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'companypanel/add_event.html', {'form': form ,  'logged_user': logged_user})




@login_required(login_url='/404/')
def event_list(request):
    logged_user = request.user
    today = timezone.now().date()  # Get today's date
    upcoming_events = Events.objects.filter(start_date__gte=today)  # Events starting today or later
    past_events = Events.objects.filter(end_date__lt=today)  # Events that ended before today
    return render(request, 'companypanel/event_list.html', {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'logged_user': logged_user
    })
    

# View to edit an event
@login_required(login_url='/404/')
def edit_event(request, event_id):
    logged_user = request.user
    event = get_object_or_404(Events, id=event_id)  # Get the event or return 404 if not found
    if request.method == 'POST':
        event_form = EventForm(request.POST, request.FILES, instance=event)  # Populate the form with POST data
        if event_form.is_valid():
            event_form.save()
            messages.success(request, 'Event successfully edited.')
            return redirect('completed_events')  # Redirect to the completed events list after saving
    else:
        event_form = EventForm(instance=event)  # Populate the form with existing event data
    
    return render(request, 'companypanel/edit_event.html', {
        'form': event_form,
        'event': event,
        'logged_user': logged_user
    })



@login_required(login_url='/404/')
def delete_event(request, event_id):
    logged_user = request.user
    event = get_object_or_404(Events, id=event_id)
    event.delete()
    messages.success(request, 'Event successfully deleted.')
    return redirect('completed_events')



@login_required(login_url='/404/')
def edit_venue(request, venue_id):
    logged_user = request.user
    venue = get_object_or_404(Venue, id=venue_id)  # Get the venue or return 404 if not found
    if request.method == 'POST':
        venue_form = VenueForm(request.POST, request.FILES, instance=venue)  # Populate the form with POST data
        if venue_form.is_valid():
            venue_form.save()
            messages.success(request, 'Venue successfully edited.')
            return redirect('venue_list')  # Redirect to venue list after saving
    else:
        venue_form = VenueForm(instance=venue)  # Populate the form with existing venue data
    return render(request, 'companypanel/edit_venue.html', {'form': venue_form , 'logged_user': logged_user})



@login_required(login_url='/404/')
def delete_venue(request, venue_id):
    logged_user = request.user
    venue = get_object_or_404(Venue, id=venue_id)  # Get the venue or return 404 if not found
    if request.method == 'POST':
        venue.delete()
        messages.success(request, 'Venue successfully deleted.')
        return redirect('venue_list')  # Redirect to venue list after deletion
    return render(request, 'companypanel/delete_venue.html', {'venue': venue , ' logged_user':  logged_user})



def completed_events(request):
    logged_user = request.user
    today = timezone.now().date()  # Get today's date
    completed_events = Events.objects.filter(end_date__lt=today)  # Filter events that have ended
    return render(request, 'companypanel/completed_events.html', {'completed_events': completed_events , 'logged_user':logged_user})








def report_page(request):
    logged_user = request.user
    # Total number of events
    total_events = Events.objects.count()

    # Total tickets booked
    total_tickets_booked = BookNoww.objects.aggregate(total_tickets=Sum('number_of_seats'))['total_tickets'] or 0

    # Total amount received
    total_amount_received = BookNoww.objects.aggregate(total_amount=Sum('ticket_price'))['total_amount'] or 0.0

    # Event with the most tickets booked
    top_event = (
        BookNoww.objects.values('event__title')
        .annotate(total_tickets=Sum('number_of_seats'))
        .order_by('-total_tickets')
        .first()
    )

    return render(request, 'companypanel/report_page.html', {
        'total_events': total_events,
        'total_tickets_booked': total_tickets_booked,
        'total_amount_received': total_amount_received,
        'top_event': top_event,
        'logged_user': logged_user
    })



@login_required(login_url='/404/')
def user_list(request):
    logged_user = request.user
    # Filter users to only include those where is_staff is False
    users = User.objects.filter(is_staff=False)
    return render(request, 'companypanel/user_list.html', {'users': users, 'logged_user': logged_user})


@login_required(login_url='/404/')
def view_user(request, user_id):
    logged_user = request.user
    user = get_object_or_404(User, id=user_id)  # Get the user or return 404
    attendee = get_object_or_404(Attendee, user=user)  # Get the attendee profile or return 404
    bookings = BookNoww.objects.filter(user=user) 




    return render(request, 'companypanel/view_user.html', {
        'user': user,
        'attendee': attendee,
        'logged_user': logged_user,
        'bookings': bookings,
    })



def total_bookings_list(request):
    logged_user = request.user
    # Get all bookings
    bookings = BookNoww.objects.all()

    context = {
        'bookings': bookings,
        'logged_user': logged_user,
    }
    
    return render(request, 'companypanel/total_bookings_list.html', context)


def ticket_type_list(request):
    logged_user = request.user
    # Fetch all ticket bookings

    today = timezone.now().date()

    # Filter events starting from today onwards
    events_with_ticket_count = Events.objects.filter(start_date__gte=today).annotate(total_tickets=Sum('bookings__number_of_seats'))
    

    # Calculate the total number of each type of ticket
    total_starter = BookNoww.objects.filter(ticket_type='starter').aggregate(total_starter=Sum('number_of_seats'))['total_starter'] or 0
    total_standard = BookNoww.objects.filter(ticket_type='standard').aggregate(total_standard=Sum('number_of_seats'))['total_standard'] or 0
    total_platinum = BookNoww.objects.filter(ticket_type='platinum').aggregate(total_platinum=Sum('number_of_seats'))['total_platinum'] or 0

    return render(request, 'companypanel/ticket_type_list.html', {
        'events_with_ticket_count': events_with_ticket_count,
        'total_starter': total_starter,
        'total_standard': total_standard,
        'total_platinum': total_platinum,
        'logged_user': logged_user
    })



# OTP Request View
class companyOTPRequestView(FormView):
    template_name = 'companypanel/companyotp_form.html'
    form_class = companyOTPForm

    def get_form_kwargs(self):
        kwargs = super(companyOTPRequestView, self).get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass the logged-in user to the form
        return kwargs

    def form_valid(self, form):
        otp = form.send_otp_email()  # This will send the OTP via email
        self.request.session['otp'] = otp  # Store OTP in session
        self.request.session['username'] = form.cleaned_data['name']  # Store username in session
        return redirect(reverse('companyverify_otp'))

# OTP Verification View
def companyverify_otp_view(request):
    logged_user = request.user
    if request.method == "POST":
        input_otp = request.POST.get('otp')  # Get OTP input from user
        session_otp = request.session.get('otp')  # Retrieve OTP from session
        username = request.session.get('username')  # Retrieve username from session
        
        if not username:
            return HttpResponse("Username not found in session.", status=400)

        if input_otp == str(session_otp):  # If OTP matches
            # OTP verified, redirect to reset password page
            return redirect(reverse('resetcompany_password', kwargs={'username': username}))
        else:
            messages.error(request, "Invalid OTP. Please try again.")
    
    return render(request, 'companypanel/companyotp_verify.html' , {'logged_user':logged_user})

# Reset Password View
def resetcompany_password(request, username):
    logged_user = request.user
    try:
        user = User.objects.get(username=username)  # Get user based on the username
    except User.DoesNotExist:
        messages.error(request, 'User does not exist.')
        return redirect('company_login')

    if request.method == 'POST':
        form = companyNewPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()  # Save the new password
            messages.success(request, 'Your password has been reset successfully!')
            return redirect('company_login')
    else:
        form = companyNewPasswordForm(user)

    return render(request, 'companypanel/companyreset_password.html', {'form': form, 'username': username , 'logged_user' : logged_user})






# Views for forgot password
def companyforgot_password(request):
    logged_user = request.user
    return render(request,'companypanel/companyforgot_password.html' , {'logged_user':  logged_user})






# View to log out the user  
@login_required(login_url='/404/')
def company_logout(request):
    logout(request)  # Log out the user
    return redirect('home')
