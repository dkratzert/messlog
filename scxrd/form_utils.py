from crispy_forms.layout import HTML

backbutton = '{% include "scxrd/buttons/small_buttons/back_to_start.html" %}'


def card(header_title, button=''):
    return HTML('<div class="card w-100 mb-3">  <div class="card-header">{} {}</div>'.format(header_title, button))
