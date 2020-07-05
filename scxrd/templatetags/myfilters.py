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
def was_refined(experiments) -> bool:
    print(experiments.count(), '1')
    if experiments.count() == 0:
        return False
    print([x.ciffilemodel.cif_exists() for x in experiments])
    return any([x.ciffilemodel.cif_exists() for x in experiments])


@register.filter
def was_measured(experiments) -> bool:
    try:
        return any([x.was_measured for x in experiments.all()])
    except Exception as e:
        print('Error in "was_measured" filter:', e)
        return False


@register.filter
def was_deposited(experiments) -> bool:
    try:
        return any([x.ciffilemodel.cif_exists for x in experiments.all()])
    except Exception as es:
        print('Error in "was_deposited" filter:', e)
        return False
