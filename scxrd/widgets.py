from django.forms import widgets
from django.utils import formats


class DateInput(widgets.DateInput):
    class Media:
        pass
        """js = (
            'flatpickr-4.5.2.min.js',
            'myjs/dateTimeInput.js',
        )
        css = {'all': (
            'flatpickr-4.5.2.min.css',
        )}"""

    input_type = 'text'
    format_index = 0

    def render(self, name, value, attrs=None, renderer=None):
        if attrs:
            format = formats.get_format(
                self.format_key
            )[self.format_index]
            attrs.update({
                'class'           : attrs.get('class', '') + ' flatpickr',
                'data-date-format': format.replace('%', '').replace('M', 'i'),
            })

            if hasattr(self, 'additional_attrs'):
                attrs.update(self.additional_attrs)

            if value:
                attrs.update({
                    'data-default-date': self.format_value(value)
                })
        return super().render(name, value, attrs)


class DateTimeInput(DateInput):
    additional_attrs = {
        'data-time_24hr'  : 'true',
        'data-enable-time': 'true',
    }

    format_index = 0
    format_key = 'DATETIME_INPUT_FORMATS'
