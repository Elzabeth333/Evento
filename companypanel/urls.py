from django.urls import  path
from django.conf.urls.static import static

from .views import company_home , companyOTPRequestView, companyverify_otp_view, companyforgot_password , resetcompany_password , total_bookings_list ,  user_list , view_user , company_logout , ticket_type_list ,  edit_venue , completed_events ,  edit_event , report_page , delete_venue , company_inbox ,  delete_event , event_list , delete_message , add_event , deleted_messages_view , add_venue , venue_list ,  company_sent_details , new_compose , message_detail , company_sent_items , company_compose_message


urlpatterns = [
    path('', company_home, name='company_home'),  # Main page for company home
    path('chat/<int:user_id>/', company_home, name='manager_chat'),  # Chat page for a specific manager
    path('send_message/', company_home, name='send_message'),  # Handle message sending
    path('company_inbox/', company_inbox, name='company_inbox'),
    path('compose_message/', company_compose_message, name='company_compose_message'),
    path('company_inbox/', company_inbox , name='company_inbox'),
    path('message/<int:message_id>/', message_detail, name='company_message_detail'),
    path('company_logout/',company_logout , name='company_logout'),
    path('company_sent_items/', company_sent_items , name='company_sent_items'),
    path('new_compose/', new_compose , name='new_compose'),
    path('company_sent_details/<int:message_id>/', company_sent_details , name='company_sent_details'),
    path('delete-message/<int:message_id>/', delete_message, name='delete_message'),
    path('deleted_messages_view/', deleted_messages_view , name='deleted_messages_view'),
    path('venue_list/', venue_list , name='venue_list'),
    path('add_venue/', add_venue , name='add_venue'),
    path('events/add/', add_event , name='add_event'),
    path('event_list/', event_list, name='event_list'),
    path('edit_event/<int:event_id>/', edit_event, name='edit_event'),  # URL for editing events
    path('delete_event/<int:event_id>/', delete_event, name='delete_event'),  # URL for deleting events
    path('edit_venue/<int:venue_id>/', edit_venue, name='edit_venue'),
    path('delete_venue/<int:venue_id>/', delete_venue, name='delete_venue'),
    path('completed-events/', completed_events, name='completed_events'),
    path('ticket_types/', ticket_type_list, name='ticket_type_list'),
    path('report/', report_page, name='report_page'),
    path('users/', user_list, name='user_list'),
    path('viewuser/<int:user_id>/', view_user, name='view_user'),
    path('totalbookings/', total_bookings_list, name='total_bookings_list'),
    path('request-otp/', companyOTPRequestView.as_view(), name='companyrequest_otp'),
    path('verify-otp/', companyverify_otp_view, name='companyverify_otp'),
    path('reset-password/<str:username>/', resetcompany_password, name='resetcompany_password'),
    path('companyforgot/', companyforgot_password , name ='companyforgot_password'),

]





