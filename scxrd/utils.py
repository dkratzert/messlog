import hashlib
from math import radians, cos, sin, sqrt

import gemmi


def generate_sha256(file):
    """
    Generates a sha256 chcksum from a FileField file handle.
    """
    f = file.open('rb')
    myhash = hashlib.sha3_256()
    if f.multiple_chunks():
        for chunk in f.chunks(chunk_size=64 * 2 ** 10):
            myhash.update(chunk)
    else:
        myhash.update(f.read())
    f.close()
    return myhash.hexdigest()


def frac_to_cart(frac_coord, cell):
    """
    Converts fractional coordinates to cartesian coodinates
    :param frac_coord: [float, float, float]
    :param cell:       [float, float, float, float, float, float]
    """
    a, b, c, alpha, beta, gamma = cell
    x, y, z = frac_coord
    alpha = radians(alpha)
    beta = radians(beta)
    gamma = radians(gamma)
    cosastar = (cos(beta) * cos(gamma) - cos(alpha)) / (sin(beta) * sin(gamma))
    sinastar = sqrt(1 - cosastar ** 2)
    Xc = a * x + (b * cos(gamma)) * y + (c * cos(beta)) * z
    Yc = 0 + (b * sin(gamma)) * y + (-c * sin(beta) * cosastar) * z
    Zc = 0 + 0 + (c * sin(beta) * sinastar) * z
    return [Xc, Yc, Zc]


def vol_unitcell(a: float, b: float, c: float, al: float, be: float, ga: float):
    """
    calculates the volume of a unit cell

    >>> v = vol_unitcell(2, 2, 2, 90, 90, 90)
    >>> print(v)
    8.0

    """
    return a * b * c * sqrt(1 + 2 * cos(radians(al)) * cos(radians(be)) * cos(radians(ga))
                            - cos(radians(al)) ** 2 - cos(radians(be)) ** 2 - cos(radians(ga)) ** 2)


# A list of minimal item that should be defined in a final cif file:
# Maybe as a dict where the value can be a method to perform actions to fill out the value e.g. for
# _refine_ls_extinction_coef: find in res file if extinction was refined.
minimal_cif_items = {'_chemical_formula_moiety': '',
                     '_space_group_crystal_system': '',
                     '_cell_measurement_reflns_used': '',
                     '_cell_measurement_theta_min': '',
                     '_cell_measurement_theta_max': '',
                     '_exptl_crystal_description': '',
                     '_exptl_crystal_colour': '',
                     '_exptl_absorpt_correction_type': '',
                     '_exptl_absorpt_correction_T_min': '',
                     '_exptl_absorpt_correction_T_max': '',
                     # the page should give a hint that SIZE in SHELXL can fill out some values:
                     '_shelx_estimated_absorpt_T_min': '',
                     '_exptl_absorpt_process_details': '',
                     '_exptl_absorpt_special_details': '',
                     '_diffrn_ambient_temperature': '',   # I could try to determine the temp if it is room or lower
                     '_diffrn_source': '',
                     '_refine_ls_extinction_coef': '',
                     'x': '',
                     'y': '',
                     }

COLOUR_CHOICES = (
    (0, 'not applicable'),
    (1, 'colourless'),
    (2, 'white'),
    (3, 'black'),
    (4, 'gray'),
    (5, 'brown'),
    (6, 'red'),
    (7, 'pink'),
    (8, 'orange'),
    (9, 'yellow'),
    (10, 'green'),
    (11, 'blue'),
    (12, 'violet')
)

COLOUR_MOD_CHOICES = (
    (0, 'not applicable'),
    (1, 'light'),
    (2, 'dark'),
    (3, 'whitish'),
    (4, 'blackish'),
    (5, 'grayish'),
    (6, 'brownish'),
    (7, 'reddish'),
    (8, 'pinkish'),
    (9, 'orangish'),
    (10, 'yellowish'),
    (11, 'greenish'),
    (12, 'bluish')
)

COLOUR_LUSTRE_COICES = (
    (0, 'not applicable'),
    (1, 'metallic'),
    (2, 'dull'),
    (3, 'clear'),
)

"""
From https://www.iucr.org/__data/iucr/cifdic_html/1/cif_core.dic/Ichemical_absolute_configuration.html

rm	    Absolute configuration established by the structure determination of a compound containing a 
        chiral reference molecule of known absolute configuration.

ad	    Absolute configuration established by anomalous-dispersion effects in diffraction measurements on the crystal.

rmad	Absolute configuration established by the structure determination of a compound containing 
        a chiral reference molecule of known absolute configuration and confirmed by anomalous-dispersion effects 
        in diffraction measurements on the crystal.

syn	    Absolute configuration has not been established by anomalous-dispersion effects in diffraction 
        measurements on the crystal. The enantiomer has been assigned by reference to an unchanging 
        chiral centre in the synthetic procedure.

unk	    Absolute configuration is unknown, there being no firm chemical evidence for its assignment to hand 
        and it having not been established by anomalous-dispersion effects in diffraction measurements on the crystal. 
        An arbitrary choice of enantiomer has been made.
.	    Inapplicable.
"""
ABSOLUTE_CONFIGURATION_CHOICES = (
    ('ad', 'Anomalous dispersion'),
    ('rm', 'Reference Molecule'),
    ('rmad', 'Reference Molecule and anomalous dispersion'),
    ('syn', 'Synthesis'),
    ('unk', 'Unknown'),
    ('.', 'Inapplicable'),
)

# _refine_ls_hydrogen_treatment
REFINE_LS_HYDROGEN_TREATMENT = (
    ('undef', "H-atom parameters not defined"),
    ('mixed', "some constrained, some independent"),
    ('constr', 'H-atom parameters constrained'),
    ('noref', 'no refinement of H-atom parameters'),
    ('refall', 'refined all H-atom parameters'),
    ('refxyz', 'refined H-atom coordinates only'),
    ('refU', "refined H-atom U's only"),
    ('hetero', 'H-atom parameters constrained for H on C, all<wbr> H-atom parameters refined for H on heteroatoms'),
    ('heteroxyz', "H-atom parameters constrained for H on C, refined H-atom coordinates only for H on heteroatoms"),
    ('heteroU', "H-atom parameters constrained for H on C, refined H-atom U's only for H on heteroatoms"),
    ('heteronoref', "H-atom parameters constrained for H on C, "
                    "no refinement of H-atom parameters for H on heteroatoms"),
    ('hetero-mixed',
     "H-atom parameters constrained for H on C and some heteroatoms, "
     "refined H-atom coordinates only for H on remaining heteroatoms"),
    ('heteroxyz-mixed',
     'H-atom parameters constrained for H on C and some heteroatoms, '
     'refined H-atom coordinates only for H on remaining heteroatoms'),
    ('heteroU-mixed',
     "H-atom parameters constrained for H on C and some heteroatoms, "
     "refined H-atom U's only for H on remaining heteroatoms"),
    ('heteronoref-mixed',
     "H-atom parameters constrained for H on C and some heteroatoms, "
     "no refinement of H-atom parameters for H on remaining heteroatoms"),
)


def get_float(line: str) -> (int, None):
    try:
        return float(line.split('(')[0].split(' ')[0])
    except (ValueError, AttributeError):
        return None


def get_int(line: str) -> (int, None):
    """
    >>> get_int("34829")
    34829
    """
    try:
        return int(line.split('(')[0].split(' ')[0])
    except (ValueError, AttributeError):
        return None


st = r''';
Olex2 1.2
(compiled 2018.04.26 svn.r3504 for OlexSys, GUI svn.r5492)
;'''


def get_string(line: str):
    """
    >>> get_string("';foo bar;'")
    'foo bar'
    >>> get_string(st)
    '\\nOlex2 1.2\\n(compiled 2018.04.26 svn.r3504 for OlexSys, GUI svn.r5492)\\n'
    >>> get_string('.')
    '.'
    >>> get_string('?')
    '?'
    >>> get_string("'?'")
    '?'
    >>> get_string('P').split()[0][:1]
    'P'
    """
    try:
        # I do this, because gemmi returns strings with quotes:
        return line.strip("';")
    except AttributeError:
        return ''


def get_table(block, items: [list, tuple]) -> gemmi.cif.Table:
    """
    items is a list of loop header to find in the loop. This method is only for testing.
    table = block.find(['_atom_type_symbol', '_atom_type_description', '_atom_type_scat_dispersion_real'])

    >>> import gemmi
    >>> cif_block = gemmi.cif.read_file("testfiles/p21c.cif").sole_block()
    >>> t = get_table(cif_block, ("_space_group_symop_operation_xyz",))
    >>> [i.str(0) for i in t]
    ['x, y, z', '-x, y+1/2, -z+1/2', '-x, -y, -z', 'x, -y-1/2, z-1/2']
    >>> '\\n'.join([i.str(0) for i in get_table(cif_block, ("_space_group_symop_operation_xyz",))])
    'x, y, z\\n-x, y+1/2, -z+1/2\\n-x, -y, -z\\nx, -y-1/2, z-1/2'
    """
    return block.find(items)
