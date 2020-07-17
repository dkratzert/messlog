from pathlib import Path

from django.conf import settings

settings.configure()
import django

django.setup()

from scxrd.models.cif_model import CifFileModel

cifdblist = []
ciffilelist = []


def get_cif_db_list():
    for cif in CifFileModel.objects.all():
        if cif.cif_exists:
            cifdblist.append(cif.cif_file_path)


def get_cif_file_list():
    for file in Path(settings.MEDIA_ROOT).rglob('*.cif'):
        ciffilelist.append(file)


if __name__ == '__main__':
    get_cif_db_list()
    get_cif_file_list()
    for file in ciffilelist:
        if file not in cifdblist:
            print(file, 'file.unlink()')
