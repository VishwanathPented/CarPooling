from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('rides/', views.ride_list, name='ride_list'),
    path('create/', views.create_ride, name='create_ride'),
    path('request/<int:ride_id>/', views.request_ride, name='request_ride'),
    path('rate/<int:ride_id>/<int:user_id>/', views.rate_user, name='rate_user'),
    path('my-rides/', views.my_rides, name='my_rides'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('find_matches/', views.find_matches, name='find_matches'),
    path('messages/', views.messages_view, name='messages'),
    path('conversation/<int:user_id>/', views.conversation, name='conversation'),
    # Remove the duplicate path and add a proper send_message URL
    path('send_message/<int:recipient_id>/', views.send_message, name='send_message'),
    path('unread_count/', views.unread_count, name='unread_count'),
    path('accept-request/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject-request/<int:request_id>/', views.reject_request, name='reject_request'),
]