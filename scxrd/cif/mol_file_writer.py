"""
MOl V3000 format
"""
import os

from scxrd.cif.atoms import get_radius_from_element


def distance(x1, y1, z1, x2, y2, z2, round_out=False):
    """
    distance between two points in space for orthogonal axes.
    >>> distance(1, 1, 1, 2, 2, 2, 4)
    1.7321
    >>> distance(1, 0, 0, 2, 0, 0, 4)
    1.0
    """
    from math import sqrt
    d = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)
    if round_out:
        return round(d, round_out)
    else:
        return d


class MolFile(object):
    """
    This mol file writer is only to use the file with JSmol, not to implement the standard exactly!
    """

    def __init__(self, atoms: list, bonds = None):
        self.atoms = atoms
        if bonds:
            self.bonds = bonds
        else:
            self.bonds = self.get_conntable_from_atoms()
        self.bondscount = len(self.bonds)
        self.atomscount = len(self.atoms)

    def header(self) -> str:
        """
        For JSmol, I don't need a facy header.
        """
        return "{}{}{}".format(os.linesep, os.linesep, os.linesep)

    def connection_table(self) -> str:
        """
          6  6  0  0  0  0  0  0  0  0  1 V3000
        """
        tab = "{:>5d}{:>5d}".format(self.atomscount, self.bondscount)
        return tab

    def get_atoms_string(self) -> str:
        """
        Returns a string with an atom in each line.
        X Y Z Element
        """
        atoms = []
        for num, at in enumerate(self.atoms):
            atoms.append("{:>10.4f}{:>10.4f}{:>10.4f} {:<2s}".format(at[5], at[6], at[7], at[1]))
        return '\n'.join(atoms)

    def get_bonds_string(self) -> str:
        """
        This is not accodingly to the file standard!
        The standard wants to have fixed format 3 digits for the bonds.
        """
        blist = []
        for bo in self.bonds:
            # This is deviating from the standard:
            blist.append("{:>4d}{:>4d}  1  0  0  0  0".format(bo[0], bo[1]))
        return '\n'.join(blist)

    def get_conntable_from_atoms(self, extra_param=0.48):
        """
        returns a connectivity table from the atomic coordinates and the covalence
        radii of the atoms.
        a bond is defined with less than the sum of the covalence radii plus the extra_param:
        :param extra_param: additional distance to the covalence radius
        :type extra_param: float
        """
        conlist = []
        for num1, at1 in enumerate(self.atoms, 1):
            at1_part = at1[8]
            rad1 = get_radius_from_element(at1[1])
            for num2, at2 in enumerate(self.atoms, 1):
                at2_part = at2[8]
                if at1_part * at2_part != 0 and at1_part != at2_part:
                    continue
                if at1[0] == at2[0]:  # name1 = name2
                    continue
                d = distance(at1[5], at1[6], at1[7], at2[5], at2[6], at2[7])
                if d > 4.0:  # makes bonding faster (longer bonds do not exist)
                    continue
                rad2 = get_radius_from_element(at2[1])
                if (rad1 + rad2) + extra_param > d:
                    if at1[1] == 'H' and at2[1] == 'H':
                        continue
                    # The extra time for this is not too much:
                    if [num2, num1] in conlist:
                        continue
                    conlist.append([num1, num2])
        return conlist

    def footer(self) -> str:
        """
        """
        return "M  END{}$$$$".format(os.linesep)

    def make_mol(self):
        """
        Combines all above to a mol file.
        """
        header = '\n\n'
        connection_table = self.connection_table()
        atoms = self.get_atoms_string()
        bonds = self.get_bonds_string()
        footer = self.footer()
        mol = "{0}{5}{1}{5}{2}{5}{3}{5}{4}".format(header, connection_table, atoms, bonds, footer, '\n')
        return mol
