from django.urls import  path
from .views import admin_home , admin_logout , adminOTPRequestView, cancelled_bookings_view , adminverify_otp_view, adminvenue_details , adminevent_detail ,  adminedit_event , adminforgot_password , resetadmin_password , adminreset_password , adminreport_page , adminticket_type_list , admincompleted_events , admindelete_venue , adminedit_venue ,  admindelete_event , adminevent_list , adminadd_event , adminvenue_list , adminadd_venue , activate_user ,   deactivate_user ,  unread_notifications , mark_all_as_read , admin_profile_pic , sidebar_search , admin_mailbox , admin_sent_items , admin_delete_message , admin_deleted_messages , delete_user , admin_message_detail , activate_company , admin_messages , sent_message_detail ,  sent_messages ,  admin_compose , manager_list ,  manager_detail 

urlpatterns = [
    path('',admin_home , name='admin_home'),
    path('chat/<int:user_id>/', admin_home, name='admin_chat'),
    path('adminsend_message/', admin_home, name='adminsend_message'),
    path('admin_logout/',admin_logout , name='admin_logout'),
    path('admin_mailbox/', admin_mailbox , name='admin_mailbox'),
    path('admin_messages/', admin_messages, name='admin_messages'),
    path('admin_message_detail/<int:message_id>/', admin_message_detail, name='admin_message_detail'),
    path('activate/<int:user_id>/', activate_company, name='activate_company'),
    path('admin_compose/', admin_compose , name='admin_compose'),
    path('manager_list/', manager_list, name='manager_list'),
    path('activate_user/<int:user_id>/', activate_user, name='activate_user'),
    path('deactivate_user/<int:user_id>/', deactivate_user, name='deactivate_user'),
    path('manager_detail/<int:manager_id>/', manager_detail , name='manager_detail'),
    path('admin_sent_items/', admin_sent_items , name='admin_sent_items'),
    path('delete_user/<int:user_id>/', delete_user, name='delete_user'),
    path('adminforgot/', adminforgot_password , name ='adminforgot_password'),
    path('deleted-messages/', admin_deleted_messages , name='admin_deleted_messages'),
    path('sent_message_detail/<int:message_id>/', sent_message_detail , name='sent_message_detail'),
    path('admin_delete_message/<int:message_id>/', admin_delete_message, name='admin_delete_message'),  # Correct this pattern
    path('unread_notifications/', unread_notifications , name='unread_notifications'),
    path('notifications/mark-all-as-read/', mark_all_as_read , name='mark_all_as_read'),
    path('sidebar_search/', sidebar_search , name='sidebar_search'),
    path('admin_profile_pic/', admin_profile_pic , name='admin_profile_pic'),
    path('adminvenue_list/', adminvenue_list , name='adminvenue_list'),
    path('adminadd_venue/', adminadd_venue , name='adminadd_venue'),
    path('adminevents/add/', adminadd_event , name='adminadd_event'),
    path('adminevent_list/', adminevent_list, name='adminevent_list'),
    path('adminresetpassword/', adminreset_password, name='adminreset_password'),
    path('adminedit_event/<int:event_id>/', adminedit_event, name='adminedit_event'),  # URL for editing events
    path('admindelete_event/<int:event_id>/', admindelete_event, name='admindelete_event'),  # URL for deleting events
    path('adminedit_venue/<int:venue_id>/', adminedit_venue, name='adminedit_venue'),
    path('admindelete_venue/<int:venue_id>/', admindelete_venue, name='admindelete_venue'),
    path('admincompleted-events/', admincompleted_events, name='admincompleted_events'),
    path('adminticket_types/', adminticket_type_list, name='adminticket_type_list'),
    path('adminreport/', adminreport_page, name='adminreport_page'),
    path('admin/resetpassword/<str:username>/', resetadmin_password, name='resetadmin_password'),
    path('request-otp/', adminOTPRequestView.as_view(), name='adminrequest_otp'),
    path('verify-otp/', adminverify_otp_view, name='adminverify_otp'),
    path('event/<int:event_id>/', adminevent_detail , name='adminevent_detail'),
    path('venue/<int:venue_id>/', adminvenue_details, name='adminvenue_details'),  # Venue details page
    path('cancelled-bookings/', cancelled_bookings_view, name='cancelled_bookings'),

]