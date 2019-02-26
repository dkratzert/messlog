from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from scxrd.utils import generate_sha256


def validate_abs_file_extension(value):
    if not value.name.endswith('.abs'):
        raise ValidationError(_('Only .abs files are allowed to upload here.'))


class SadabsModel(models.Model):
    """
    A model for SADABS and TWINABS files
    TODO: Check if file (sha256) was already uploaded somewhere and ask if shurely upload again.
    TODO: try to get Tmin and Tmax from the hkl file in the cif file first.
    """
    abs_file = models.FileField(upload_to='abs', null=True, blank=True,
                                        validators=[validate_abs_file_extension], verbose_name='abs file')
    sha256 = models.CharField(max_length=256, blank=True, null=True)
    date_created = models.DateTimeField(verbose_name='upload date', null=True, blank=True)
    date_updated = models.DateTimeField(verbose_name='change date', null=True, blank=True)
    filesize = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sha256 = generate_sha256(self.abs_file.file)
        self.filesize = self.abs_file.size
        if not self.date_created:
            self.date_created = timezone.now()
        self.date_updated = timezone.now()
        super(SadabsModel, self).save(*args, **kwargs)

    @property
    def exists(self):
        if Path(self.abs_file.path).exists():
            return True
        return False


