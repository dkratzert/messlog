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



