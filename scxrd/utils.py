import hashlib


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





