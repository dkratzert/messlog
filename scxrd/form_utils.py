from crispy_forms.layout import ButtonHolder, Submit, HTML
from django.utils.translation import gettext_lazy as _

backbutton = """
    <a role="button" class="btn btn-sm btn-outline-secondary float-right my-0 py-0" 
        href="{% url "index" %}">
    """ + "{}</a>".format(_('Back to start'))

save_button = ButtonHolder(
    Submit('Save', 'Save', css_class='btn-primary mr-2 ml-0 mb-3'),
    # This cancel button works in combination with the FormActionMixin in views.py
    # the view is redirected to the index page if the request contains 'cancel'
    Submit('cancel', 'Cancel', css_class='btn btn-danger ml-2 mb-3', formnovalidate='formnovalidate'),
    HTML('<br>'),
)

save_button2 = ButtonHolder(
    Submit('Save', 'Save', css_class='btn-primary mr-2'),
    HTML('''<a href="{% url 'scxrd:index' %}" class="btn btn-outline-danger" 
            formnovalidate="formnovalidate">''' + '''{}</a>
            '''.format(_('Cancel'))),
    css_class=' ml-3 mb-3'
)

submit_button = ButtonHolder(
    Submit('Save', 'Submit', css_class='btn-primary mr-2 ml-1'),
    HTML('''<a href="{% url 'scxrd:index' %}" class="btn btn-outline-danger" 
            formnovalidate="formnovalidate">''' + '''{}</a>
            '''.format(_('Cancel'))),
    css_class=' ml-3 mb-3'
)


def card(header_title, button=''):
    return HTML('<div class="card w-100 mb-3">  <div class="card-header">{} {}</div>'.format(header_title, button))

