from __future__ import unicode_literals, print_function, absolute_import, division

import json

from django.http import HttpResponse

from .models import Upload, ImageUpload
from .forms import UploadForm, ImageUploadForm


def _uploads(request, Model, Form):
    category = request.GET.get('category', '').strip().lower()

    if request.method == 'POST':
        form = Form(request.POST, request.FILES)
        if form.is_valid():
            upload = Model.objects.upload_file(form.cleaned_data['file'], category=category)
            return HttpResponse(json.dumps(upload.to_dict()), content_type='application/json')
        else:
            errors = dict((key, unicode(val[0])) for key, val in form.errors.items())
            return HttpResponse(json.dumps(errors), content_type='application/json', status=400)

    results = []
    uploads = Model.objects.filter(category=category)

    if request.GET.get('search'):
        uploads = uploads.filter(name__icontains=request.GET['search'].strip())

    for upload in uploads:
        results.append(upload.to_dict())

    return HttpResponse(json.dumps(results), content_type='application/json')


def uploads(request):
    return _uploads(request, Upload, UploadForm)


def image_uploads(request):
    return _uploads(request, ImageUpload, ImageUploadForm)

