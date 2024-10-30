from django.urls import  path
from .views import user_home , user_logout, add_blog , completed_events , userreset_password , verify_otp , completed_event_details , blog_detail_view , blog_delete_view , blog_edit_view ,  blog_list , all_events_view ,  request_otp , booking_form , booking_confirmation  , user_about , book_now_vieww ,  event_details , user_event_list , cancel_booking

urlpatterns = [
    path('',user_home , name='user_home'),
    path('events_user/', user_home , name='events_user'),
    path('events_user/', user_home , name='event_schedule'),
    path('user_about/', user_about , name='user_about'),
    path('user_event_list/', user_event_list , name='user_event_list'),
    path('user_logout/',user_logout , name='user_logout'),
    path('event/<int:event_id>/', event_details, name='event_details'),
    path('completedevent/<int:event_id>/', completed_event_details, name='completed_event_details'),
    path('book/<int:event_id>/', booking_form, name='booking_form'),
    path('request_otp/', request_otp, name='request_otp'),
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('userbooking_confirmation/', booking_confirmation, name='booking_confirmation'),
    path('cancel_booking/<int:booking_id>/', cancel_booking, name='cancel_booking'),
    path('blogs/', blog_list, name='blog_list'),  # Blog list view
    path('blogs/add/', add_blog, name='add_blog'),  # Add new blog
    path('all-events/', all_events_view, name='all_events'),
    path('blog/<int:blog_id>/', blog_detail_view, name='blog_detail'),
    path('blog/<int:blog_id>/edit/', blog_edit_view, name='blog_edit'),
    path('blog/<int:blog_id>/delete/', blog_delete_view, name='blog_delete'),
    path('user_completed-events/', completed_events, name='usercompleted_events'),
    path('user/resetpasswordd/<str:username>/', userreset_password, name='userreset_password'),
    path('book-noww/<int:event_id>/', book_now_vieww, name='book_now'),
    


]