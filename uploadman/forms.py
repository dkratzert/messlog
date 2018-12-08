from django import forms


class UploadForm(forms.Form):
    file = forms.FileField()


class ImageUploadForm(forms.Form):
    file = forms.ImageField()

