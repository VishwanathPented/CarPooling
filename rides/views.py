from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Ride, RideRequest, Rating
from .forms import RideForm, RatingForm
from .models import Route, RouteMatch
from accounts.forms import UserProfileForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    return redirect('ride_list')

@login_required
def create_ride(request):
    if request.method == 'POST':
        form = RideForm(request.POST)
        if form.is_valid():
            ride = form.save(commit=False)
            ride.driver = request.user
            ride.save()
            messages.success(request, 'Ride created successfully!')
            return redirect('ride_list')
    else:
        form = RideForm()
    return render(request, 'rides/create_ride.html', {'form': form})

@login_required
def ride_list(request):
    rides = Ride.objects.filter(departure_time__gte=timezone.now())
    return render(request, 'rides/ride_list.html', {'rides': rides})

@login_required
def request_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    if RideRequest.objects.filter(ride=ride, passenger=request.user).exists():
        messages.error(request, 'You have already requested this ride.')
    else:
        RideRequest.objects.create(ride=ride, passenger=request.user)
        messages.success(request, 'Ride request sent successfully!')
    return redirect('ride_list')

@login_required
def rate_user(request, ride_id, user_id):
    """View for rating a user after a ride."""
    from django.contrib.auth import get_user_model
    from django.contrib import messages
    User = get_user_model()
    
    ride = get_object_or_404(Ride, id=ride_id)
    user_to_rate = get_object_or_404(User, id=user_id)
    
    # Check if the current user is authorized to rate
    is_driver = request.user == ride.driver
    is_passenger = RideRequest.objects.filter(ride=ride, passenger=request.user, status='COMPLETED').exists()
    
    if not (is_driver or is_passenger):
        messages.error(request, "You are not authorized to rate for this ride.")
        return redirect('my_rides')
    
    # Check if already rated
    already_rated = Rating.objects.filter(
        from_user=request.user,
        to_user=user_to_rate,
        ride=ride
    ).exists()
    
    if already_rated:
        messages.info(request, f"You have already rated {user_to_rate.username} for this ride.")
        return redirect('my_rides')
    
    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        # Create the rating
        Rating.objects.create(
            from_user=request.user,
            to_user=user_to_rate,
            ride=ride,
            rating=rating_value,
            comment=comment
        )
        
        messages.success(request, f"Thank you for rating {user_to_rate.username}!")
        return redirect('my_rides')
    
    return render(request, 'rides/rate_user.html', {
        'user_to_rate': user_to_rate,
        'ride': ride
    })

@login_required
def my_rides(request):
    offered_rides = Ride.objects.filter(driver=request.user)
    requested_rides = RideRequest.objects.filter(passenger=request.user)
    return render(request, 'rides/my_rides.html', {
        'offered_rides': offered_rides,
        'requested_rides': requested_rides
    })

@login_required
def my_requests(request):
    sent_requests = RideRequest.objects.filter(passenger=request.user)
    received_requests = RideRequest.objects.filter(ride__driver=request.user)
    return render(request, 'rides/my_requests.html', {
        'sent_requests': sent_requests,
        'received_requests': received_requests
    })

@login_required
def accept_request(request, request_id):
    ride_request = get_object_or_404(RideRequest, id=request_id, ride__driver=request.user)
    ride_request.status = 'ACCEPTED'
    ride_request.save()
    
    # Update available seats
    ride = ride_request.ride
    ride.seats_available -= 1
    ride.save()
    
    messages.success(request, f'You have accepted the ride request from {ride_request.passenger.username}.')
    return redirect('my_requests')

@login_required
def reject_request(request, request_id):
    ride_request = get_object_or_404(RideRequest, id=request_id, ride__driver=request.user)
    ride_request.status = 'REJECTED'
    ride_request.save()
    messages.success(request, f'You have rejected the ride request from {ride_request.passenger.username}.')
    return redirect('my_requests')

@login_required
def profile(request):
    return render(request, 'rides/profile.html', {
        'user': request.user
    })


@login_required
def find_matches(request):
    """View for finding ride matches based on route proximity or time windows."""
    matches = []
    
    if request.method == 'POST':
        start_point = request.POST.get('start_point')
        end_point = request.POST.get('end_point')
        date = request.POST.get('date')
        time_window = int(request.POST.get('time_window', 2))
        role = request.POST.get('role', 'passenger')
        
        # Here you would implement the actual matching algorithm
        # For now, we'll just return all available rides as potential matches
        from .models import Ride
        from django.contrib.auth import get_user_model
        User = get_user_model()
        import random
        
        available_rides = Ride.objects.filter(seats_available__gt=0)
        
        # Simple mock matching for demonstration
        for ride in available_rides:
            # Create a mock match object
            match = {
                'ride': ride,
                'user': ride.driver,
                'role': 'driver',
                'score': random.randint(60, 95)  # Random match score for demonstration
            }
            matches.append(match)
    
    return render(request, 'rides/find_matches.html', {'matches': matches})
    # For riders looking for rides
    available_routes = Route.objects.filter(
        departure_time__gte=timezone.now(),
        available_seats__gt=0
    ).order_by('departure_time')
    
    # For drivers checking their route matches
    my_routes = Route.objects.filter(
        driver=request.user,
        departure_time__gte=timezone.now()
    )
    
    for route in my_routes:
        potential_matches = route.find_matches()
        for match in potential_matches:
            RouteMatch.objects.get_or_create(
                route=route,
                passenger=match,
                defaults={'match_score': calculate_match_score(route, match)}
            )
    
    context = {
        'available_routes': available_routes,
        'my_routes': my_routes,
    }
    return render(request, 'rides/find_matches.html', context)

def calculate_match_score(route, user):
    score = 0
    # Time preference matching
    if user.preferred_pickup_time:
        time_diff = abs(route.departure_time.time().hour - user.preferred_pickup_time.hour)
        score += max(0, 100 - (time_diff * 10))  # Deduct points for time difference
    
    # Location matching (simple contains check)
    if user.home_address.lower() in route.start_point.lower():
        score += 50
    
    return min(100, score)  # Cap score at 100


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'rides/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'rides/change_password.html', {'form': form})


@login_required
def messages_view(request):
    """View for displaying all conversations."""
    # Mock data for demonstration
    conversations = []
    
    return render(request, 'rides/messages.html', {'conversations': conversations})

def conversation(request, user_id):
    """View for displaying a conversation with a specific user."""
    # Use get_user_model() instead of directly importing User
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    other_user = User.objects.get(id=user_id)
    messages = []  # In a real app, you'd fetch messages between users
    
    return render(request, 'rides/conversation.html', {
        'other_user': other_user,
        'messages': messages
    })

@csrf_protect
@login_required
def send_message(request, recipient_id):
    # Use get_user_model() instead of directly importing User
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    recipient = get_object_or_404(User, id=recipient_id)
    
    # Handle GET requests - show conversation
    if request.method == 'GET':
        # Get all messages between the current user and the recipient
        from .models import Message  # Import the Message model
        
        messages = Message.objects.filter(
            (Q(sender=request.user) & Q(recipient=recipient)) |
            (Q(sender=recipient) & Q(recipient=request.user))
        ).order_by('timestamp')
        
        context = {
            'messages': messages,
            'other_user': recipient
        }
        return render(request, 'rides/conversation.html', context)
    
    # Handle POST requests - send message
    elif request.method == 'POST':
        content = request.POST.get('message', '')
        
        if content:
            from .models import Message  # Import the Message model
            
            message = Message.objects.create(
                sender=request.user,
                recipient=recipient,
                content=content
            )
            
            return JsonResponse({
                'status': 'success',
                'message_id': message.id
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Message content cannot be empty'
            })
    
    # Handle other methods
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

def unread_count(request):
    """API endpoint to get the number of unread messages."""
    from django.http import JsonResponse
    # In a real app, you'd query the database for unread messages
    count = 0
    
    return JsonResponse({'count': count})
