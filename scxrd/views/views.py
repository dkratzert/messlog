from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView
from django_robohash.robotmaker import make_robot_svg

from scxrd.cif.cif_file_io import CifContainer
from scxrd.cif.mol_file_writer import MolFile
from scxrd.cif.sdm import SDM
from scxrd.models.cif_model import CifFileModel
from scxrd.models.measurement_model import Measurement
from scxrd.utils import randstring


class ResidualsTable(DetailView):
    """
    Show residuals of the in-table selected measurement by ajax request.
    """
    model = Measurement
    template_name = 'scxrd/residuals_table.html'


class MoleculeView(LoginRequiredMixin, View):
    """
    View to get atom data as .mol file.
    """

    def post(self, request: WSGIRequest, *args, **kwargs):
        exp_id = request.POST.get('measurement_id')
        try:
            cif = CifFileModel.objects.get(measurement=exp_id)
        except ObjectDoesNotExist:
            return self.show_robot()
        cif_path = cif.cif_file_path
        if not cif.cif_exists:
            return self.show_robot()
        grow = request.POST.get('grow')
        cif = CifContainer(cif_path)
        if cif.atoms_fract:
            return HttpResponse(self.make_molfile(cif, grow))
        return HttpResponse('')

    def show_robot(self):
        # Show a robot where no cif is found:
        robot = make_robot_svg(randstring(), width=300, height=300)
        return HttpResponse(robot[1:])

    def make_molfile(self, cif: CifContainer, grow: str) -> str:
        """
        Returns a mol file with the molecule from the CIF file.
        :param cif: The CIF object
        :param grow: wheather to grow or not
        :return: molfile string
        """
        molfile = ' '
        if grow == 'true':
            sdm = SDM(list(cif.atoms_fract), cif.symmops, cif.cell[:6], centric=cif.is_centrosymm)
            try:
                needsymm = sdm.calc_sdm()
                atoms = sdm.packer(sdm, needsymm)
            except Exception as e:
                print('Error in SDM:', e)
                return molfile
        else:
            atoms = cif.atoms_orth
        try:
            molfile = MolFile(atoms)
            molfile = molfile.make_mol()
        except (TypeError, KeyError):
            print("Error while writing mol file.")
        return molfile

    # always reload complete molecule:
    @never_cache
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
