from django import template
from django.contrib.auth.models import User

register = template.Library()


@register.filter
def is_operator(user: User):
    return user.profile.is_operator


@register.filter
def is_superuser(user: User):
    return user.is_superuser


@register.filter
def was_refined(measurements) -> bool:
    if measurements.count() == 0:
        return False
    print([x.ciffilemodel.cif_exists for x in measurements])
    return any([x.ciffilemodel.cif_exists for x in measurements])


@register.filter
def was_measured(measurements) -> bool:
    try:
        return any([x.was_measured for x in measurements.all()])
    except Exception as e:
        print('Error in "was_measured" filter:', e)
        return False


@register.filter
def was_deposited(measurements) -> bool:
    try:
        return any([x.ciffilemodel.cif_exists for x in measurements.all()])
    except Exception as e:
        print('Error in "was_deposited" filter:', e)
        return False
