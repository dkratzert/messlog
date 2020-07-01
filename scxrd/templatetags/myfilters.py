from django import template
from django.contrib.auth.models import User

register = template.Library()


@register.filter
def is_operator(user: User):
    return user.profile.is_operator


@register.filter
def is_superuser(user: User):
    return user.is_superuser
