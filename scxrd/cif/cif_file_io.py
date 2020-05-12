#  ----------------------------------------------------------------------------
#  "THE BEER-WARE LICENSE" (Revision 42):
#  daniel.kratzert@ac.uni-freiburg.de> wrote this file.  As long as you retain
#  this notice you can do whatever you want with this stuff. If we meet some day,
#  and you think this stuff is worth it, you can buy me a beer in return.
#  Dr. Daniel Kratzert
#  ----------------------------------------------------------------------------
from pathlib import Path
# noinspection PyUnresolvedReferences
from typing import Dict, List, Tuple, Union

import gemmi


class CifContainer():
    """
    This class holds the content of a cif file, independent of the file parser used.
    """

    def __init__(self, file: Path):
        self.fileobj = file
        # I do this in small steps instead of gemmi.cif.read_file() in order to
        # leave out the check_for_missing_values. This was gemmi reads cif files
        # with missing values.
        self.doc = self.read_file(str(self.fileobj.absolute()))
        self.block = self.doc.sole_block()
        # will not ok with non-ascii characters in the res file:
        self.chars_ok = True
        try:
            self.resdata = self.block.find_value('_shelx_res_file')
        except UnicodeDecodeError:
            # This is a fallback in case _shelx_res_file has non-ascii characters.
            print('File has non-ascii characters. Switching to compatible mode.')
            self.doc = self.read_string(self.fileobj.read_text(encoding='cp1250', errors='ignore'))
            self.block = self.doc.sole_block()
            self.resdata = self.block.find_value('_shelx_res_file')
            self.chars_ok = False
        self.doc.check_for_duplicates()
        self.atomic_struct = gemmi.make_small_structure_from_block(self.block)
        # A dictionary to convert Atom names like 'C1_2' or 'Ga3' into Element names like 'C' or 'Ga'
        self._name2elements = dict(
            zip(self.block.find_loop('_atom_site_label'), self.block.find_loop('_atom_site_type_symbol')))

    def read_file(self, path: str) -> gemmi.cif.Document:
        """
        Reads a cif file and returns a gemmi document object.
        :param path: path to the file
        :return: gemmi document
        """
        doc = gemmi.cif.Document()
        doc.source = path
        doc.parse_file(path)
        return doc

    def read_string(self, cif_string: str) -> gemmi.cif.Document:
        """
        Reads a cif file from a string and returns a gemmi cif docment.
        :param cif_string: cif as string
        :return: gemmi document
        """
        doc = gemmi.cif.Document()
        doc.parse_string(cif_string)
        return doc

    def __getitem__(self, item: str) -> str:
        result = self.block.find_value(item)
        if result:
            if result == '?' or result == "'?'":
                return ''
            # TODO: can I do this?:
            # return retranslate_delimiter(result)
            return gemmi.cif.as_string(result)
        else:
            return ''

    def __delitem__(self, key):
        self.block.find_pair_item(key).erase()

    def save(self, filename: str = None) -> None:
        """
        Saves the current cif file in the specific order of the order list.
        :param filename:  Name to save cif file to.
        """
        if not filename:
            filename = str(self.fileobj.absolute())
        self.doc.write_file(filename, gemmi.cif.Style.Indent35)
        # Path(filename).write_text(self.doc.as_string(gemmi.cif.Style.Indent35))

    @property
    def loops(self):
        loops = []
        for b in self.block:
            if b.loop:
                l = b.loop
                loops.append(l)
        return loops

    @property
    def Z_value(self):
        return self.atomic_struct.cell.volume / self.atomic_struct.cell.volume_per_image()

    def _spgr(self) -> gemmi.SpaceGroup:
        if self.symmops:
            symm_ops = self.symmops
        else:
            symm_ops = self.symmops_from_spgr
        return gemmi.find_spacegroup_by_ops(gemmi.GroupOps([gemmi.Op(o) for o in symm_ops]))

    @property
    def space_group(self) -> str:
        """
        Returns the space group from the symmetry operators.
        spgr.short_name() gives the short name.
        """
        try:
            return self._spgr().xhm()
        except (AttributeError, RuntimeError):
            if self['_space_group_name_H-M_alt']:
                return self['_space_group_name_H-M_alt'].strip("'")
            else:
                return ''

    @property
    def symmops_from_spgr(self) -> List[str]:
        # _symmetry_space_group_name_Hall
        space_group = None
        if self['_space_group_name_H-M_alt']:
            space_group = self['_space_group_name_H-M_alt']
        if self['_symmetry_space_group_name_H-M']:
            space_group = self['_symmetry_space_group_name_H-M']
        if not space_group:
            return []
        ops = [op.triplet() for op in
               gemmi.find_spacegroup_by_name(gemmi.cif.as_string(space_group)).operations()]
        return ops

    @property
    def spgr_number_from_symmops(self) -> int:
        return self._spgr().number

    @property
    def crystal_system(self) -> str:
        if not self._spgr():
            return ''
        return self._spgr().crystal_system_str()

    @property
    def hall_symbol(self) -> str:
        return self._spgr().hall

    @property
    def hkl_checksum_calcd(self) -> int:
        """
        Calculates the shelx checksum for the hkl file content of a cif file.

        #>>> c = CifContainer(Path('test-data/DK_zucker2_0m.cif'))
        #>>> c.hkl_checksum_calcd
        #69576
        #>>> c = CifContainer(Path('test-data/4060310.cif'))
        #>>> c.hkl_checksum_calcd
        #0
        """
        hkl = self.block.find_value('_shelx_hkl_file')
        if hkl:
            return self.calc_checksum(hkl[1:-1])
        else:
            return 0

    @property
    def res_checksum_calcd(self) -> int:
        """
        Calculates the shelx checksum for the res file content of a cif file.

        #>>> c = CifContainer(Path('test-data/DK_zucker2_0m.cif'))
        #>>> c.res_checksum_calcd
        #52593
        #>>> c = CifContainer(Path('test-data/4060310.cif'))
        #>>> c.res_checksum_calcd
        #0
        """
        res = self.block.find_value('_shelx_res_file')
        if res:
            return self.calc_checksum(res[1:-1])
        return 0

    @staticmethod
    def calc_checksum(input_str: str) -> int:
        """
        Calculates the shelx checksum of a cif file.
        """
        sum = 0
        try:
            input_str = input_str.encode('cp1250', 'ignore')
        except Exception:
            input_str = input_str.encode('ascii', 'ignore')
        for char in input_str:
            # print(char)
            if char > 32:  # ascii 32 is space character
                sum += char
        sum %= 714025
        sum = sum * 1366 + 150889
        sum %= 714025
        sum %= 100000
        return sum

    def rename_data_name(self, newname: str = ''):
        """
        Reanmes data_ tags to the newname. Also _vrf tags are renamed accordingly.
        http://journals.iucr.org/services/cif/checking/checkfaq.html
        """
        newname = ''.join([i for i in newname if i.isascii()])
        self.block.name = newname
        for item in self.block:
            if item.pair is not None:
                key, value = item.pair
                if key.startswith('_vrf'):
                    newkey = '_' + '_'.join(key.split('_')[1:3]) + '_' + newname
                    self.block.find_pair_item(key).erase()
                    self.block.set_pair(newkey, value)

    @property
    def symmops(self) -> List[str]:
        """
        Reads the symmops from the cif file.

        >>> cif = CifContainer(Path('test-data/DK_ML7-66-final.cif'))
        >>> cif.symmops
        ['x, y, z', '-x, -y, -z']
        """
        xyz1 = self.block.find(("_symmetry_equiv_pos_as_xyz",))  # deprecated
        xyz2 = self.block.find(("_space_group_symop_operation_xyz",))  # New definition
        if xyz1:
            return [i.str(0) for i in xyz1]
        elif xyz2:
            return [i.str(0) for i in xyz2]
        else:
            return []

    @property
    def is_centrosymm(self) -> bool:
        """
        >>> from scxrd.cif.cif_file_io import CifContainer
        >>> from pathlib import Path
        >>> c = CifContainer(Path('test-data/DK_zucker2_0m-finalcif.cif'))
        >>> c.is_centrosymm
        False
        >>> c = CifContainer(Path('test-data/DK_ML7-66-final.cif'))
        >>> c.is_centrosymm
        True
        """
        ops = gemmi.GroupOps([gemmi.Op(o) for o in self.symmops])
        return ops.is_centric()

    @property
    def atoms_fract(self) -> List:
        for at in self.atomic_struct.sites:
            yield {'name': at.label, 'symbol': at.type_symbol, 'x': at.fract.x, 'y': at.fract.y, 'z': at.fract.z,
                   'part': at.disorder_group, 'occ': at.occ, 'uiso': at.u_iso}

    @property
    def atoms_orth(self):
        cell = self.atomic_struct.cell
        for at in self.atomic_struct.sites:
            x, y, z = at.orth(cell)
            yield {'name': at.label, 'symbol': at.type_symbol, 'x': x, 'y': y, 'z': z,
                   'part': at.disorder_group, 'occ': at.occ, 'uiso': at.u_iso}

    @property
    def hydrogen_atoms_present(self) -> bool:
        for at in self.atomic_struct.sites:
            if at.type_symbol in ('H', 'D'):
                return True
        else:
            return False

    @property
    def disorder_present(self) -> bool:
        for at in self.atomic_struct.sites:
            if at.disorder_group:
                return True
        else:
            return False

    @property
    def cell(self) -> tuple:
        c = self.atomic_struct.cell
        return c.a, c.b, c.c, c.alpha, c.beta, c.gamma, c.volume

    def ishydrogen(self, label: str) -> bool:
        hydrogen = ('H', 'D')
        if self.iselement(label) in hydrogen:
            return True
        else:
            return False

    def atoms(self, without_h: bool = False) -> Tuple[str, str, str, str, str, str, str, str]:
        labels = self.block.find_loop('_atom_site_label')
        types = self.block.find_loop('_atom_site_type_symbol')
        x = self.block.find_loop('_atom_site_fract_x')
        y = self.block.find_loop('_atom_site_fract_y')
        z = self.block.find_loop('_atom_site_fract_z')
        part = self.block.find_loop('_atom_site_disorder_group')
        occ = self.block.find_loop('_atom_site_occupancy')
        u_eq = self.block.find_loop('_atom_site_U_iso_or_equiv')
        for label, type, x, y, z, part, occ, ueq in zip(labels, types, x, y, z, part, occ, u_eq):
            if without_h and self.ishydrogen(label):
                continue
            #         0    1   2  3  4   5   6     7
            yield label, type, x, y, z, part, occ, ueq

    def bonds(self, without_H: bool = False):
        """
        Yields a list of bonds in the cif file.
        """
        label1 = self.block.find_loop('_geom_bond_atom_site_label_1')
        label2 = self.block.find_loop('_geom_bond_atom_site_label_2')
        dist = self.block.find_loop('_geom_bond_distance')
        symm = self.block.find_loop('_geom_bond_site_symmetry_2')
        for label1, label2, dist, symm in zip(label1, label2, dist, symm):
            if without_H and (self.ishydrogen(label1) or self.ishydrogen(label2)):
                continue
            else:
                yield (label1, label2, dist, symm)

    def angles(self, without_H: bool = False):
        label1 = self.block.find_loop('_geom_angle_atom_site_label_1')
        label2 = self.block.find_loop('_geom_angle_atom_site_label_2')
        label3 = self.block.find_loop('_geom_angle_atom_site_label_3')
        angle = self.block.find_loop('_geom_angle')
        symm1 = self.block.find_loop('_geom_angle_site_symmetry_1')
        symm2 = self.block.find_loop('_geom_angle_site_symmetry_3')
        for label1, label2, label3, angle, symm1, symm2 in zip(label1, label2, label3, angle, symm1, symm2):
            if without_H and (self.ishydrogen(label1) or self.ishydrogen(label2) or self.ishydrogen(label3)):
                continue
            else:
                yield (label1, label2, label3, angle, symm1, symm2)

    def iselement(self, name: str) -> str:
        return self._name2elements[name]

    def natoms(self, without_h: bool = False) -> int:
        return len(list(self.atoms(without_h)))

    def nbonds(self, without_h: bool = False) -> int:
        """
        Number of bonds in the cif object, with and without hydrogen atoms.
        """
        return len(list(self.bonds(without_h)))

    def nangles(self, without_h: bool = False) -> int:
        """
        Number of bond angles in the cif object, with and without hydrogen atoms.
        """
        return len(list(self.angles(without_h)))

    def ntorsion_angles(self, without_h: bool = False) -> int:
        """
        Number of torsion angles in the cif object, with and without hydrogen atoms.
        """
        return len(list(self.torsion_angles(without_h)))

    def torsion_angles(self, without_h: bool = False):
        label1 = self.block.find_loop('_geom_torsion_atom_site_label_1')
        label2 = self.block.find_loop('_geom_torsion_atom_site_label_2')
        label3 = self.block.find_loop('_geom_torsion_atom_site_label_3')
        label4 = self.block.find_loop('_geom_torsion_atom_site_label_4')
        torsang = self.block.find_loop('_geom_torsion')
        symm1 = self.block.find_loop('_geom_torsion_site_symmetry_1')
        symm2 = self.block.find_loop('_geom_torsion_site_symmetry_2')
        symm3 = self.block.find_loop('_geom_torsion_site_symmetry_3')
        symm4 = self.block.find_loop('_geom_torsion_site_symmetry_4')
        # publ = self.block.find_loop('_geom_torsion_publ_flag')
        for label1, label2, label3, label4, torsang, symm1, symm2, symm3, symm4 in zip(label1, label2, label3, label4,
                                                                                       torsang, symm1, symm2, symm3,
                                                                                       symm4):
            if without_h and (self.ishydrogen(label1) or self.ishydrogen(label2)
                              or self.ishydrogen(label3) or self.ishydrogen(label3)):
                continue
            yield label1, label2, label3, label4, torsang, symm1, symm2, symm3, symm4

    def hydrogen_bonds(self):
        label_d = self.block.find_loop('_geom_hbond_atom_site_label_D')
        label_h = self.block.find_loop('_geom_hbond_atom_site_label_H')
        label_a = self.block.find_loop('_geom_hbond_atom_site_label_A')
        dist_dh = self.block.find_loop('_geom_hbond_distance_DH')
        dist_ha = self.block.find_loop('_geom_hbond_distance_HA')
        dist_da = self.block.find_loop('_geom_hbond_distance_DA')
        angle_dha = self.block.find_loop('_geom_hbond_angle_DHA')
        symm = self.block.find_loop('_geom_hbond_site_symmetry_A')
        # publ = self.block.find_loop('_geom_hbond_publ_flag')
        for label_d, label_h, label_a, dist_dh, dist_ha, dist_da, angle_dha, symm in zip(label_d, label_h, label_a,
                                                                                         dist_dh, dist_ha, dist_da,
                                                                                         angle_dha, symm):
            yield label_d, label_h, label_a, dist_dh, dist_ha, dist_da, angle_dha, symm

    def key_value_pairs(self):
        """
        Returns the key/value pairs of a cif file sorted by priority.

        >>> c = CifContainer(Path('test-data/P21c-final.cif'))
        >>> c.key_value_pairs()[:2]
        [['_audit_contact_author_address', '?'], ['_audit_contact_author_email', '?']]
        """
        high_prio_no_values, high_prio_with_values = self.get_keys()
        return high_prio_no_values + [['These below are already in:', '---------------------']] + high_prio_with_values

    def is_centrokey(self, key):
        """
        Is True if the kurrent key is only valid 
        for non-centrosymmetric structures
        """
        non_centrosymm_keys = ('_chemical_absolute_configuration', '_refine_ls_abs_structure_Flack',
                               '_refine_ls_abs_structure_details')
        return self.is_centrosymm and key in non_centrosymm_keys

    def get_keys(self):
        """
        Returns the keys to be displayed in the main table as two separate lists.
        """
        questions = []
        # contains the answered keys:
        with_values = []
        # holds keys that are not in the cif file but in essential_keys:
        missing_keys = []
        for item in self.block:
            if item.pair is not None:
                key, value = item.pair
                if len(value) > 1000:
                    # do not include res and hkl file:
                    continue
                if key.startswith('_shelx'):
                    continue
                if self.is_centrokey(key):
                    continue
                if not value or value == '?' or value == "'?'":
                    questions.append([key, value])
                else:
                    with_values.append([key, value])
        all_keys = [x[0] for x in with_values] + [x[0] for x in questions]
        # check if there are keys not in the cif but in essential_keys:
        return sorted(questions), sorted(with_values)

    def add_to_cif(self, key: str, value: str = '?'):
        """
        Add an additional key value pair to the cif block.
        """
        self.block.set_pair(key, value)

    def test_checksums(self) -> str:
        """
        A method to check wether the checksums in the cif file fit to the content.
        """
        cif_res_ckecksum = 0
        if self.res_checksum_calcd > 0:
            cif_res_ckecksum = self.block.find_value('_shelx_res_checksum') or -1
            cif_res_ckecksum = int(cif_res_ckecksum)
        if cif_res_ckecksum > 0 and cif_res_ckecksum != self.res_checksum_calcd:
            return 'SHELX .res file checksum failed!'
        cif_hkl_ckecksum = 0
        if self.hkl_checksum_calcd > 0:
            cif_hkl_ckecksum = self.block.find_value('_shelx_hkl_checksum') or -1
            cif_hkl_ckecksum = int(cif_hkl_ckecksum)
        if cif_hkl_ckecksum > 0 and cif_hkl_ckecksum != self.hkl_checksum_calcd:
            return 'SHELX .cif file checksum failed!'
