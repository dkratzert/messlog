from django.contrib import admin

# Register your models here.
from polls.models import Measurement, Machine
from .models import Question, Choice



class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']
    empty_value_display = 'unknown'
    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date']}),
    ]
    inlines = [ChoiceInline]



admin.site.register(Question, QuestionAdmin)
admin.site.register(Measurement)
admin.site.register(Machine)