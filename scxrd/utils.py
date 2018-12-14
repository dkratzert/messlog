import hashlib
import datetime


def generate_sha256(file):
    f = file.open('rb')
    hash = hashlib.sha3_256()
    if f.multiple_chunks():
        for chunk in f.chunks(chunk_size=64 * 2 ** 10):
            hash.update(chunk)
    else:
        hash.update(f.read())
    f.close()
    sha1 = hash.hexdigest()
    return sha1



