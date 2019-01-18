import time

import gemmi
from pathlib import Path

p = Path(r'D:\tmp\manycifs')
cfiles = p.glob('*.cif')

errors = []
nerr = 0
nf = 0

t1 = time.perf_counter()


for n, f in enumerate(cfiles):
    nf = n
    try:
        struct = gemmi.cif.read_file(str(f))
    except RuntimeError as e:
        print(e)
        nerr += 1
        errors.append(e)
        continue
    try:
        b = struct.sole_block()
    except (RuntimeError, IndexError) as e:
        print(e)
        errors.append(e)
        nerr += 1
        continue
    su = b.find_value('_chemical_formula_sum')
    print(su)

t2 = time.perf_counter()
print('##############################')
for e in errors:
    print(e)

print('----')

print(nf, 'files with', nerr, 'errors. In', t2 - t1, 's.')
