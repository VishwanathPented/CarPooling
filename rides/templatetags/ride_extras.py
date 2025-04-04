from django import template
from rides.models import get_user_average_rating, get_user_recent_ratings

register = template.Library()

@register.filter
def get_average_rating(user):
    return get_user_average_rating(user)

@register.filter
def get_recent_ratings(user):
    return get_user_recent_ratings(user)