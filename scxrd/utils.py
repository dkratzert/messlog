import base64
import hashlib
import os
from math import radians, cos, sin, sqrt

import gemmi
from django.core.files import File


def randstring():
    """A random string for robohash"""
    return base64.b32encode(os.urandom(3))[:5].decode('utf-8')


def generate_sha256(file: File):
    """
    Generates a sha256 chcksum from a FileField file handle.
    """
    # f = file.open('rb')
    myhash = hashlib.sha3_256()
    if file.multiple_chunks():
        for chunk in file.chunks(chunk_size=64 * 2 ** 10):
            myhash.update(chunk)
    else:
        myhash.update(file.read())
    # file.close()
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


COLOUR_CHOICES = (
    (0, '----------'),
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


def get_float(line: str) -> (float, None):
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


st = b''';
Olex2 1.2
(compiled 2018.04.26 svn.r3504 for OlexSys, GUI svn.r5492)
;'''


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
