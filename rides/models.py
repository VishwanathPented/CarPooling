from django.db import models
from django.conf import settings
from datetime import timedelta

class Route(models.Model):
    start_point = models.CharField(max_length=255)
    end_point = models.CharField(max_length=255)
    departure_time = models.DateTimeField()
    return_time = models.DateTimeField(null=True, blank=True)
    max_passengers = models.IntegerField(default=4)
    available_seats = models.IntegerField(default=4)
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='routes_as_driver')
    passengers = models.ManyToManyField(settings.AUTH_USER_MODEL, through='RouteMatch', related_name='routes_as_passenger')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def find_matches(self):
        from django.db.models import Q
        time_window = timedelta(minutes=30)  # Configurable time window
        
        potential_matches = CustomUser.objects.filter(
            Q(home_address__icontains=self.start_point) |  # Similar starting point
            Q(preferred_pickup_time__range=(
                self.departure_time - time_window,
                self.departure_time + time_window
            ))
        ).exclude(id=self.driver.id)
        
        return potential_matches

class RouteMatch(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ]
    
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    match_score = models.FloatField(default=0)  # Higher score means better match
    created_at = models.DateTimeField(auto_now_add=True)

class Ride(models.Model):
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rides_offered')
    start_point = models.CharField(max_length=200)
    end_point = models.CharField(max_length=200)
    departure_time = models.DateTimeField()
    seats_available = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.start_point} to {self.end_point} on {self.departure_time}"

class RideRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),  # Add a completed status
    ]
    
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)
    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_rated_by_passenger(self):
        """Check if the passenger has rated the driver for this ride."""
        return Rating.objects.filter(
            from_user=self.passenger,
            to_user=self.ride.driver,
            ride=self.ride
        ).exists()
    
    def is_rated_by_driver(self):
        """Check if the driver has rated the passenger for this ride."""
        return Rating.objects.filter(
            from_user=self.ride.driver,
            to_user=self.passenger,
            ride=self.ride
        ).exists()

class Rating(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings_given')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings_received')
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Ensure a user can only rate another user once per ride
        unique_together = ('from_user', 'to_user', 'ride')
    
    def __str__(self):
        return f"{self.from_user} rated {self.to_user} {self.rating}/5 for ride {self.ride}"

# Add a method to the User model to get average rating
from django.db.models import Avg

def get_user_average_rating(user):
    """Get the average rating for a user."""
    avg_rating = Rating.objects.filter(to_user=user).aggregate(Avg('rating'))
    return avg_rating['rating__avg'] or 0

# Add a method to get recent ratings
def get_user_recent_ratings(user, limit=5):
    """Get the most recent ratings for a user."""
    return Rating.objects.filter(to_user=user).order_by('-created_at')[:limit]

from django.conf import settings

# Add this to your models.py file if it doesn't exist already
class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Message from {self.sender} to {self.recipient} at {self.timestamp}"
