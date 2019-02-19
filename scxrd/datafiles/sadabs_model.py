from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from scxrd.utils import generate_sha256


def validate_abs_file_extension(value):
    if not value.name.endswith('.cif'):
        raise ValidationError(_('Only .cif files are allowed to upload here.'))


class SadabsModel(models.Model):
    """
    A model for SADABS and TWINABS files
    """
    abs_file_on_disk = models.FileField(upload_to='abs', null=True, blank=True,
                                        validators=[validate_abs_file_extension], verbose_name='abs file')
    sha256 = models.CharField(max_length=256, blank=True, null=True)
    date_created = models.DateTimeField(verbose_name='upload date', null=True, blank=True)
    date_updated = models.DateTimeField(verbose_name='change date', null=True, blank=True)
    filesize = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        try:
            self.sha256 = generate_sha256(self.abs_file_on_disk.file)
            self.filesize = self.abs_file_on_disk.size
        except ValueError:
            pass
        if not self.date_created:
            self.date_created = timezone.now()
        self.date_updated = timezone.now()
        super().save(*args, **kwargs)
