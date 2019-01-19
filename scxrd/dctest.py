
st = r''';
Olex2 1.2
(compiled 2018.04.26 svn.r3504 for OlexSys, GUI svn.r5492)
;'''


def foo():
    r"""
    # Testing gemmi unit cell methods:
    >>> import gemmi
    >>> cell = gemmi.UnitCell(25.14, 39.50, 45.07, 90, 90, 90)
    >>> cell
    <gemmi.UnitCell(25.14, 39.5, 45.07, 90, 90, 90)>
    >>> cell.fractionalize(gemmi.Position(10, 10, 10))
    <gemmi.Fractional(0.397772, 0.253165, 0.221877)>
    >>> cell.orthogonalize(gemmi.Fractional(0.5, 0.5, 0.5))
    <gemmi.Position(12.57, 19.75, 22.535)>
    >>> gemmi.cif.as_number('0.123(2)')
    0.12300000000000001

    #>>> gemmi.cif.is_null('.')  # Not available?
    #>>> gemmi.cif.is_null('?')
    >>> gemmi.cif.as_string(st)
    '\nOlex2 1.2\n(compiled 2018.04.26 svn.r3504 for OlexSys, GUI svn.r5492)'
    >>> from scxrd.utils import get_string
    >>> get_string("';foo bar;'")
    'foo bar'
    >>> get_string(st)
    '\nOlex2 1.2\n(compiled 2018.04.26 svn.r3504 for OlexSys, GUI svn.r5492)\n'
    """