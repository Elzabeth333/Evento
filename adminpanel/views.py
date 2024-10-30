from django.shortcuts import render , redirect
from django.contrib.auth import authenticate , login , logout , update_session_auth_hash
from django.contrib.auth.decorators import login_required , user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User ,  Group 
from django.contrib import messages
from userpanel.models import Blog
from django.db.models import Sum
from django.utils import timezone
from sitevisitor.forms import MessageForm
from .forms import MessageForm , ProfilePictureForm , EventForm , VenueForm , PasswordResetForm , adminOTPForm
from django.urls import reverse
from django.http import Http404
from django.db.models import Q
from django.views.generic.edit import FormView
from django.db.models import OuterRef, Subquery
from django.http import JsonResponse
from django.http import Http404
from django.http import HttpResponseBadRequest
from .forms import adminNewPasswordForm 
from django.http import HttpResponse
from .tasks import send_welcome_email  # Import the Celery task
from .models import  Notification ,  Message , BookNoww  , Company , Profile , Events , TicketType , Venue # Assuming you have a Notification model


@login_required(login_url='/404/')
def admin_home(request, user_id=None):
    logged_user = request.user

    # Handle sending a new message
    # Handle sending a new message (adminsend_message logic)
    if request.method == 'POST':
        message_text = request.POST.get('message')
        receiver_id = request.POST.get('receiver_id')

        if not receiver_id or not message_text:
            return HttpResponseBadRequest("Missing necessary parameters")

        try:
            receiver = get_object_or_404(User, pk=receiver_id)
        except ValueError:
            return HttpResponseBadRequest("Invalid user ID provided")

        # Create a new message
        Message.objects.create(sender=request.user, receiver=receiver, body=message_text)

        # Redirect back to the chat page with the receiver
        return redirect('admin_chat', user_id=receiver.id)
    # Fetch notifications and messages
    notifications = Message.objects.filter(sender__is_active=False, is_deleted=False).order_by('-created_at')
    notification_count = notifications.count()

    sent_messages = Message.objects.filter(sender=request.user)
    received_messages = Message.objects.filter(receiver=request.user)

    user_ids = set(sent_messages.values_list('receiver_id', flat=True)) | set(received_messages.values_list('sender_id', flat=True))
    users = User.objects.filter(id__in=user_ids).exclude(id=request.user.id)

    user_unread_counts = {
        user.id: Message.objects.filter(sender=user, receiver=request.user, is_read=False, is_deleted=False).count()
        for user in users
    }

    message_notifications = Message.objects.filter(receiver=request.user, is_read=False, is_deleted=False, sender__is_active=True).order_by('-created_at')[:5]
    message_notifications_count = message_notifications.count()

    # Fetch manager group and users
    manager_group = Group.objects.get(name='Manager')
    manager_users = User.objects.filter(is_superuser=False, is_staff=True, groups=manager_group).select_related('company')

    # Subquery for the latest message
    latest_message_subquery = Message.objects.filter(sender=OuterRef('pk')).order_by('-created_at').values('subject', 'created_at')[:1]

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
        selected_user = get_object_or_404(User, id=user_id)
        messages = Message.objects.filter(
            sender__in=[request.user, selected_user],
            receiver__in=[request.user, selected_user],
            is_deleted=False
        ).order_by('created_at')

    # Get chat users and manager users
    chat_manager_users = User.objects.filter(
        is_superuser=False, is_staff=True, groups=manager_group
    ).select_related('company').annotate(
        last_message_subject=Subquery(latest_message_subquery.values('subject')[:1]),
        last_message_date=Subquery(latest_message_subquery.values('created_at')[:1])
    )

    # Fetch other necessary data for the admin dashboard
    venues_list = Venue.objects.all()
    total_events = Events.objects.count()
    total_tickets_booked = BookNoww.objects.aggregate(total_tickets=Sum('number_of_seats'))['total_tickets'] or 0
    total_amount_received = BookNoww.objects.aggregate(total_amount=Sum('ticket_price'))['total_amount'] or 0.0
    top_event = BookNoww.objects.values('event__title').annotate(total_tickets=Sum('number_of_seats')).order_by('-total_tickets').first()
    total_blogs = Blog.objects.count()
    total_users = User.objects.filter(is_staff=False).count()
    completed_events = Events.objects.filter(end_date__lt=timezone.now()).count()
    upcoming_events = Events.objects.filter(start_date__gte=timezone.now()).count()
    upcoming_eventss = Events.objects.filter(start_date__gte=timezone.now())


    context = {
        'logged_user': logged_user,
        'venues_list': venues_list,
        'total_amount_received': total_amount_received,
        'total_blogs': total_blogs,
        'total_tickets_booked': total_tickets_booked,
        'total_users': total_users,
        'top_event': top_event,
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'upcoming_eventss': upcoming_eventss,
        'completed_events': completed_events,
        'chat_manager_users': chat_manager_users,
        'manager_users': manager_users,
        'notifications': notifications,
        'selected_user': selected_user,
        'messages': messages,
        'notification_count': notification_count,
        'users': users,
        'user_unread_counts': user_unread_counts,
        'message_notifications': message_notifications,
        'message_notifications_count': message_notifications_count,
    }

    return render(request, 'adminpanel/admin_home.html', context)



@login_required(login_url='/404/')
def activate_company(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.user.is_superuser:  # Ensure only superusers can activate accounts
        if not user.is_active:
            user.is_active = True
            user.save()
            messages.success(request, f'Company manager {user.username} has been activated successfully.')
            
            # Trigger the Celery task to send the welcome email
            send_welcome_email.delay(user.email, user.username)

        else:
            messages.info(request, f'Company manager {user.username} is already active.')
    else:
        messages.error(request, 'You do not have permission to activate this account.')

    return redirect('admin_messages')  # Redirect back to the messages page or wherever appropriate



@login_required(login_url='/404/')
def admin_mailbox(request):
    logged_user = request.user
    query = request.GET.get('mailbox_search', '')  # Get the search query from the form

    notifications = Message.objects.filter(sender__is_active=True, is_deleted=False).order_by('-created_at')
    notification_count = notifications.count()

    sent_messages = Message.objects.filter(sender=request.user)
    received_messages = Message.objects.filter(receiver=request.user)

    user_ids = set(sent_messages.values_list('receiver_id', flat=True)) | set(received_messages.values_list('sender_id', flat=True))
    users = User.objects.filter(id__in=user_ids).exclude(id=request.user.id)

    user_unread_counts = {
        user.id: Message.objects.filter(sender=user, receiver=request.user, is_read=False, is_deleted=False).count()
        for user in users
    }

    message_notifications = Message.objects.filter(
        receiver=request.user, 
        is_read=False, 
        is_deleted=False, 
        sender__is_active=True
    ).exclude(subject="New Company Registration").order_by('-created_at')[:5]
    message_notifications_count = message_notifications.count()

    # Fetch messages where the current user is the receiver and apply the search query
    if query:
        messages = Message.objects.filter(
            Q(receiver=request.user),  # The current user is the receiver
            Q(subject__icontains=query) | Q(body__icontains=query) | Q(sender__username__icontains=query),
            is_deleted=False
        ).order_by('-created_at')
    else:
        messages = Message.objects.filter(receiver=request.user, is_deleted=False).order_by('-created_at')

    context = {
        'logged_user': logged_user,
        'notifications': notifications,
        'notification_count': notification_count,
        'users': users,
        'user_unread_counts': user_unread_counts,
        'message_notifications': message_notifications,
        'message_notifications_count': message_notifications_count,
        'messages': messages,
    }
    return render(request, 'adminpanel/admin_mailbox.html', context)





@login_required(login_url='/404/')
def sidebar_search(request):
    query = request.GET.get('q', '')  # Get the search query from the GET parameters
    results = []

    if query:
        # Example search for users and messages, adjust based on your models and search needs
        user_results = User.objects.filter(Q(username__icontains=query) | Q(email__icontains=query))
        message_results = Message.objects.filter(Q(subject__icontains=query) | Q(body__icontains=query))
        results = list(user_results) + list(message_results)  # Combine results into a single list

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'adminpanel/search_results.html', context)



@login_required(login_url='/404/')
def admin_messages(request):
    logged_user = request.user
    notifications = Message.objects.filter(sender__is_active=False , is_deleted=False).order_by('-created_at')
    notification_count = notifications.count()

    sent_messages = Message.objects.filter(sender=request.user)
    received_messages = Message.objects.filter(receiver=request.user)

    user_ids = set(sent_messages.values_list('receiver_id', flat=True)) | set(received_messages.values_list('sender_id', flat=True))

    users = User.objects.filter(id__in=user_ids).exclude(id=request.user.id)

    user_unread_counts = {
        user.id: Message.objects.filter(sender=user, receiver=request.user, is_read=False ,is_deleted=False).count()
        for user in users
    }

    message_notifications = Message.objects.filter(receiver=request.user, is_read=False , is_deleted=False , sender__is_active=True ).order_by('-created_at')[:5]
    message_notifications_count = message_notifications.count()
    # Fetch messages where the current user is the receiver and not marked as deleted
    messages = Message.objects.filter(sender__is_active=False, is_deleted=False).order_by('-created_at')
    

    context = {
        'logged_user' : logged_user,
        'notifications': notifications,
        'notification_count': notification_count,
        'users': users,
        'user_unread_counts': user_unread_counts,
        'message_notifications': message_notifications,
        'message_notifications_count': message_notifications_count,
        'messages' : messages ,
    }
    # Fetch messages where the sender is inactive and not marked as deleted
    
    return render(request, 'adminpanel/admin_messages.html', context)


@login_required(login_url='/404/')
def admin_sent_items(request):
    logged_user = request.user
    query = request.GET.get('senttable_search', '')  # Get the search query from the form

    # Filter to show only non-deleted messages sent by the logged-in admin
    if query:
        sent_messages = Message.objects.filter(
            sender=request.user, 
            is_deleted=False
        ).filter(
            Q(subject__icontains=query) | Q(body__icontains=query) | Q(receiver__username__icontains=query)
        ).order_by('-created_at')
    else:
        sent_messages = Message.objects.filter(sender=request.user, is_deleted=False).order_by('-created_at')

    return render(request, 'adminpanel/admin_sent_items.html', {'sent_messages': sent_messages, 'logged_user': logged_user})

@login_required(login_url='/404/')
def admin_delete_message(request, message_id):
    try:
        message = get_object_or_404(Message, id=message_id)
        print(f"Message found: {message}")  # Debugging output
        if request.method == 'POST':
            message.is_deleted = True
            message.deleted_at = timezone.now()
            message.save()
            return redirect('admin_mailbox')
    except Message.DoesNotExist:
        print(f"Message with ID {message_id} does not exist.")  # Debugging output
    return redirect('admin_mailbox')


@login_required(login_url='/404/')
def admin_message_detail(request, message_id):
    message = get_object_or_404(Message, id=message_id, receiver=request.user)
    if not message.is_read:
        message.is_read = True
        message.save()
    return render(request, 'adminpanel/admin_message_detail.html', {'message': message})


@login_required(login_url='/404/')
def sent_message_detail(request, message_id):
    # Try to get the message where the user is either the sender or the receiver
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    return render(request, 'adminpanel/sent_message_detail.html', {'message': message})


@login_required(login_url='/404/')
def admin_deleted_messages(request):
    logged_user = request.user
    # Filter to show only messages marked as deleted for the logged-in admin
    deleted_messages = Message.objects.filter(sender=request.user, is_deleted=True).order_by('-deleted_at')
    return render(request, 'adminpanel/admin_deleted_messages.html', {'deleted_messages': deleted_messages, 'logged_user': logged_user})



@login_required(login_url='/404/')
def delete_user(request, user_id):
    """
    View to delete a user.
    """
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User has been deleted successfully.')
        return redirect(reverse('admin_user_list'))  # Adjust this URL name as needed

    return redirect(reverse('admin_user_list'))  # Adjust this URL name as needed


@login_required(login_url='/404/')
def admin_compose(request):
    messages = Message.objects.filter(receiver=request.user, is_deleted=False ).order_by('-created_at')
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            to_user_input = form.cleaned_data.get('to')
            subject = form.cleaned_data.get('subject')
            body = form.cleaned_data.get('body')

            try:
                recipient = User.objects.get(username=to_user_input)
            except User.DoesNotExist:
                try:
                    recipient = User.objects.get(email=to_user_input)
                except User.DoesNotExist:
                    form.add_error('to', 'User not found.')
                    return render(request, 'adminpanel/admin_compose.html', {'form': form})

            message = Message(
                sender=request.user,
                receiver=recipient,
                subject=subject,
                body=body,
            )
            message.save()

            return redirect('admin_mailbox')
    else:
        form = MessageForm()

    return render(request, 'adminpanel/admin_compose.html', {'form': form , 'messages': messages})


@login_required(login_url='/404/')
def sent_messages(request):
    sent_messages = Message.objects.filter(sender=request.user).order_by('-created_at')
    return render(request, 'adminpanel/sent_message.html', {'sent_messages': sent_messages})



@login_required(login_url='/404/')
def manager_list(request):
    query = request.GET.get('admintable_search', '')

    try:
        # Attempt to retrieve the 'Manager' group
        manager_group = Group.objects.get(name='Manager')
    except Group.DoesNotExist:
        # Handle the case where the 'Manager' group does not exist
        messages.error(request, "Manager group does not exist.")
        return redirect('admin_home')

    # Filter managers in the 'Manager' group
    managers = User.objects.filter(groups=manager_group)

    # Apply search filter if a query is provided
    if query:
        managers = managers.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    # Fetch the companies associated with the managers
    companies = Company.objects.filter(user__in=managers).select_related('user')

    return render(request, 'adminpanel/manager_list.html', {'managers': managers, 'companies': companies})



@login_required(login_url='/404/')
def activate_user(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
        company_manager = get_object_or_404(Company, user=user)
        
        # Activate the user
        user.is_active = True
        user.save()
        
        # Optional: Set the company manager as active or inactive based on your logic
        company_manager.is_active = True  # Change this if needed
        company_manager.save()
        
        messages.success(request, f"{user.username} has been activated successfully.")
    except Http404:
        messages.error(request, "User or Company not found.")
    
    return redirect('manager_list')



@login_required(login_url='/404/')
def deactivate_user(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
        company_manager = get_object_or_404(Company, user=user)
        
        # Deactivate the user
        user.is_active = False
        user.save()
        
        # Deactivate the company manager
        company_manager.is_active = False
        company_manager.save()
        
        messages.success(request, f"{user.username} has been deactivated successfully.")
    except Http404:
        messages.error(request, "User or Company not found.")
    
    return redirect('manager_list')






@login_required(login_url='/404/')
def manager_detail(request, manager_id):
    # Fetch the manager (user) object
    manager = get_object_or_404(User, id=manager_id)
    
    # Fetch the related company details
    company_manager = get_object_or_404(Company, user=manager)
    
    return render(request, 'adminpanel/manager_details.html', {'manager': manager, 'company_manager': company_manager})


@login_required(login_url='/404/')
def unread_notifications(request):
    # Get all unread notifications for the logged-in user
    notifications = Notification.objects.filter(user=request.user, is_read=False)

    context = {
        'notifications': notifications,
        'message_notifications_count': notifications.count(),
    }
    return render(request, 'notifications/unread_notifications.html', context)


@login_required(login_url='/404/')
def mark_all_as_read(request):
    # Mark all notifications for the logged-in user as read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('unread_notifications')



def superuser_required(view_func):
    decorated_view_func = login_required(user_passes_test(lambda u: u.is_superuser)(view_func))
    return decorated_view_func

@superuser_required
def admin_profile_pic(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('admin_home')  # Redirect to admin home or wherever appropriate
    else:
        form = ProfilePictureForm(instance=profile)
    
    context = {
        'form': form
    }
    return render(request, 'adminpanel/admin_profile_pic.html', context)


def custom_404_view(request):
    return render(request, 'sitevisitor/404.html')




def admincompleted_events(request):
    logged_user = request.user
    today = timezone.now().date()  # Get today's date
    completed_events = Events.objects.filter(end_date__lt=today)  # Filter events that have ended
    return render(request, 'adminpanel/admin_completed.html', {'completed_events': completed_events , 'logged_user':logged_user})



def adminticket_type_list(request):
    logged_user = request.user
    # Fetch all ticket bookings
    bookings = BookNoww.objects.select_related('event').all()

    # Calculate the total number of each type of ticket
    total_starter = BookNoww.objects.filter(ticket_type='starter').aggregate(total_starter=Sum('number_of_seats'))['total_starter'] or 0
    total_standard = BookNoww.objects.filter(ticket_type='standard').aggregate(total_standard=Sum('number_of_seats'))['total_standard'] or 0
    total_platinum = BookNoww.objects.filter(ticket_type='platinum').aggregate(total_platinum=Sum('number_of_seats'))['total_platinum'] or 0

    return render(request, 'adminpanel/adminticket_type_list.html', {
        'bookings': bookings,
        'total_starter': total_starter,
        'total_standard': total_standard,
        'total_platinum': total_platinum,
        'logged_user': logged_user
    })




def adminreport_page(request):
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

    return render(request, 'adminpanel/adminreport_page.html', {
        'total_events': total_events,
        'total_tickets_booked': total_tickets_booked,
        'total_amount_received': total_amount_received,
        'top_event': top_event,
        'logged_user': logged_user
    })



@login_required(login_url='/404/')
def adminevent_list(request):
    logged_user = request.user
    query = request.GET.get('eventtable_search', '')

    # Filter upcoming and past events based on the search query
    today = timezone.now().date()  # Get today's date

    # If there's a search query, filter events based on it
    if query:
        upcoming_events = Events.objects.filter(
            Q(start_date__gte=today),  # Only include upcoming events
            Q(title__icontains=query) | Q(description__icontains=query)
        )
        past_events = Events.objects.filter(
            Q(end_date__lt=today),  # Only include past events
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    else:
        # If no search query, get all upcoming and past events
        upcoming_events = Events.objects.filter(start_date__gte=today)
        past_events = Events.objects.filter(end_date__lt=today)

    return render(request, 'adminpanel/admin_eventlist.html', {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'logged_user': logged_user
    })
    

# View to edit an event
@login_required(login_url='/404/')
def adminedit_event(request, event_id):
    logged_user = request.user
    event = get_object_or_404(Events, id=event_id)  # Get the event or return 404 if not found
    if request.method == 'POST':
        event_form = EventForm(request.POST, request.FILES, instance=event)  # Populate the form with POST data
        if event_form.is_valid():
            event_form.save()
            messages.success(request, 'Event successfully edited.')
            return redirect('admincompleted_event')  # Redirect to the completed events list after saving
    else:
        event_form = EventForm(instance=event)  # Populate the form with existing event data
    
    return render(request, 'adminpanel/adminedit_event.html', {
        'form': event_form,
        'event': event,
        'logged_user': logged_user
    })




@login_required(login_url='/404/')
def admindelete_event(request, event_id):
    
    event = get_object_or_404(Events, id=event_id)
    event.delete()
    messages.success(request, 'Event successfully deleted.')
    return redirect('admincompleted_events')



@login_required(login_url='/404/')
def adminedit_venue(request, venue_id):
    logged_user = request.user
    venue = get_object_or_404(Venue, id=venue_id)  # Get the venue or return 404 if not found
    if request.method == 'POST':
        venue_form = VenueForm(request.POST, request.FILES, instance=venue)  # Populate the form with POST data
        if venue_form.is_valid():
            venue_form.save()
            messages.success(request, 'Venue successfully edited.')
            return redirect('adminvenue_list')  # Redirect to venue list after saving
    else:
        venue_form = VenueForm(instance=venue)  # Populate the form with existing venue data
    return render(request, 'adminpanel/adminedit_venue.html', {'form': venue_form , 'logged_user': logged_user})



@login_required(login_url='/404/')
def admindelete_venue(request, venue_id):
    logged_user = request.user
    venue = get_object_or_404(Venue, id=venue_id)  # Get the venue or return 404 if not found
    if request.method == 'POST':
        venue.delete()
        messages.success(request, 'Venue successfully deleted.')
        return redirect('adminvenue_list')  # Redirect to venue list after deletion
    return render(request, 'adminpanel/admindelete_venue.html', {'venue': venue , ' logged_user':  logged_user})




@login_required(login_url='/404/')
def adminvenue_list(request):
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

    return render(request, 'adminpanel/adminvenue_list.html', {'venues': venues , 'logged_user':logged_user})



@login_required(login_url='/404/')
def adminadd_venue(request):
    logged_user = request.user
    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('venue_list')
    else:
        form = VenueForm()
    return render(request, 'adminpanel/adminadd_venue.html', {'form': form , 'logged_user':logged_user})



@login_required(login_url='/404/')
def adminadd_event(request):
    logged_user = request.user
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid() :
            form.save()
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'adminpanel/adminadd_event.html', {'form': form ,  'logged_user': logged_user})





@login_required(login_url='/404/')
def adminreset_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password successfully Reset')  # Important for keeping the user logged in
            return redirect('company_login')
    else:
        form = PasswordResetForm(user=request.user)

    return render(request, 'adminpanel/adminreset_password.html', {'form': form})


# Views for forgot password
def adminforgot_password(request):
    return render(request,'adminpanel/adminforgot_password.html')




class adminOTPRequestView(FormView):
    template_name = 'adminpanel/adminotp_form.html'
    form_class = adminOTPForm

    def get_form_kwargs(self):
        # Pass the current user to the form via kwargs
        kwargs = super(adminOTPRequestView, self).get_form_kwargs()
        kwargs['user'] = self.request.user  # Add the user to the form kwargs
        return kwargs

    def form_valid(self, form):
        # Send OTP email
        otp = form.send_otp_email()
        self.request.session['otp'] = otp
        self.request.session['username'] = form.cleaned_data['name']  # Store username in session
        return redirect(reverse('adminverify_otp'))



def adminverify_otp_view(request):
    if request.method == "POST":
        input_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        username = request.session.get('username')  # Get username from session
        
        if not username:
            return HttpResponse("Username not found in session.", status=400)

        if input_otp == str(session_otp):
            # OTP is verified, redirect to reset password page
            return redirect(reverse('resetadmin_password', kwargs={'username': username}))
        else:
            return HttpResponse("Invalid OTP. Please try again.")
    
    return render(request, 'adminpanel/adminotp_verify.html')





def resetadmin_password(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, 'User does not exist.')
        return redirect('company_login')

    if request.method == 'POST':
        form = adminNewPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been reset successfully!')
            return redirect('company_login')
    else:
        form = adminNewPasswordForm(user)

    return render(request, 'adminpanel/adminreset_password.html', {'form': form, 'username': username})





@login_required(login_url='/404/')
def adminevent_detail(request, event_id):
    event = get_object_or_404(Events, id=event_id)
    
    context = {
        'event': event,
    }
    return render(request, 'adminpanel/adminevent_detail.html', context)


@login_required(login_url='/404/')
def adminvenue_details(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    
    context = {
        'venue': venue,
    }
    return render(request, 'adminpanel/adminvenue_details.html', context)


# View to edit an event
@login_required(login_url='/404/')
def adminedit_event(request, event_id):
    logged_user = request.user
    event = get_object_or_404(Events, id=event_id)  # Get the event or return 404 if not found
    if request.method == 'POST':
        event_form = EventForm(request.POST, request.FILES, instance=event)  # Populate the form with POST data
        if event_form.is_valid():
            event_form.save()
            messages.success(request, 'Event successfully edited.')
            return redirect('admincompleted_events')  # Redirect to the completed events list after saving
    else:
        event_form = EventForm(instance=event)  # Populate the form with existing event data
    
    return render(request, 'adminpanel/adminedit_event.html', {
        'form': event_form,
        'event': event,
        'logged_user': logged_user
    })



@login_required(login_url='/404/')
def admindelete_event(request, event_id):
    
    event = get_object_or_404(Events, id=event_id)
    event.delete()
    messages.success(request, 'Event successfully deleted.')
    return redirect('admincompleted_events')



@login_required(login_url='/404/')
def adminedit_venue(request, venue_id):
    logged_user = request.user
    venue = get_object_or_404(Venue, id=venue_id)  # Get the venue or return 404 if not found
    if request.method == 'POST':
        venue_form = VenueForm(request.POST, request.FILES, instance=venue)  # Populate the form with POST data
        if venue_form.is_valid():
            venue_form.save()
            messages.success(request, 'Venue successfully edited.')
            return redirect('adminvenue_list')  # Redirect to venue list after saving
    else:
        venue_form = VenueForm(instance=venue)  # Populate the form with existing venue data
    return render(request, 'adminpanel/adminedit_venue.html', {'form': venue_form , 'logged_user': logged_user})



@login_required(login_url='/404/')
def admindelete_venue(request, venue_id):
    logged_user = request.user
    venue = get_object_or_404(Venue, id=venue_id)  # Get the venue or return 404 if not found
    if request.method == 'POST':
        venue.delete()
        messages.success(request, 'Venue successfully deleted.')
        return redirect('venue_list')  # Redirect to venue list after deletion
    return render(request, 'adminpanel/admindelete_venue.html', {'venue': venue , ' logged_user':  logged_user})




def cancelled_bookings_view(request):
    cancelled_bookings = BookNoww.objects.filter(is_cancelled=True)
    return render(request, 'userpanel/cancelled_bookings.html', {
        'cancelled_bookings': cancelled_bookings
    })









# View to log out the user
def admin_logout(request):
    logout(request)  # Log out the user
    return redirect('home')



