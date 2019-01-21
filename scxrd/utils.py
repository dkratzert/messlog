import hashlib
from math import radians, cos, sin, sqrt


def generate_sha256(file):
    """
    Generates a sha256 chcksum from a FileField file handle.
    """
    f = file.open('rb')
    hash = hashlib.sha3_256()
    if f.multiple_chunks():
        for chunk in f.chunks(chunk_size=64 * 2 ** 10):
            hash.update(chunk)
    else:
        hash.update(f.read())
    f.close()
    return hash.hexdigest()


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


def get_float(line: str) -> (int, None):
    try:
        return float(line.split('(')[0].split(' ')[0])
    except ValueError:
        return None


def get_int(line: str) -> (int, None):
    try:
        return int(line.split('(')[0].split(' ')[0])
    except ValueError:
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
    '\nOlex2 1.2\n(compiled 2018.04.26 svn.r3504 for OlexSys, GUI svn.r5492)\n'
    """
    try:
        # I do this, because gemmi returns strings with quotes:
        return line.strip("';")
    except AttributeError:
        return ''
