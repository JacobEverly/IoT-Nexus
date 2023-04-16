import string
import hashlib

from py_ecc.fields import FQ
from .parameters import prime_64, prime_254, prime_255

class prime254_FQ(FQ):
    field_modulus = prime_254


class prime255_FQ(FQ):
    field_modulus = prime_255

def SHA(s):
    if isinstance(s, str):
        s_encode = s.encode()
    elif isinstance(s, int):
        FQ = prime254_FQ
        s = int(FQ(s))
        s_encode = s.to_bytes(32, byteorder="big")
    return hashlib.sha256(s_encode)
