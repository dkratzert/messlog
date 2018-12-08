import hashlib

from django.db import models
from django.core.files.storage import default_storage
from django.core.files import File
from django.conf import settings


class UploadManager(models.Manager):

    def upload_file(self, uploaded_file, category=''):
        sha256 = hashlib.sha256()
        for c in uploaded_file.chunks():
            sha256.update(c)
        checksum = sha256.hexdigest()
        inst = self.get_queryset().filter(checksum=checksum).first()

        if inst:
            return inst

        inst = self.model(
            checksum=checksum,
            category=category,
            name=uploaded_file.name,
            size=uploaded_file.size,
            content_type=uploaded_file.content_type,
        )

        filename = '{}.{}'.format(checksum, uploaded_file.content_type.split('/')[1])
        inst.upload.save(filename, File(uploaded_file))

        return inst


class AbstractUpload(models.Model):
    checksum = models.CharField(max_length=64, primary_key=True)
    category = models.CharField(max_length=255, db_index=True, default='')
    name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255, default='applicaiton/binary')
    size = models.BigIntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __unicode__(self):
        return self.name

    def get_url(self):
        return self.upload.url

    def to_dict(self):
        return {
            'checksum': self.checksum,
            'url': self.get_url(),
            'content_type': self.content_type,
            'size': self.size,
            'name': self.name,
            'created_on': self.created_on.isoformat(),
        }


def _upload_to(instance, filename):
    if instance.category:
        filename = '{}/{}'.format(instance.category.strip().replace(' ', '-'), filename)
    return '{}/{}'.format(getattr(settings, 'UPMAN_UPLOAD_PATH', 'uploads/upman'), filename)


class Upload(AbstractUpload):
    upload = models.FileField(
        upload_to=_upload_to,
        storage=default_storage
    )

    objects = UploadManager()


class ImageUpload(AbstractUpload):
    upload = models.ImageField(
        upload_to=_upload_to,
        storage=default_storage,
        width_field='width',
        height_field='height',
    )
    height = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(default=0)

    objects = UploadManager()

